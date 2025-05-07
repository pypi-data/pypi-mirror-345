from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
import json
import re
import textwrap
from relationalai.clients.config import Config
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel.rel_utils import sanitize_identifier
from . import builder as b, annotations as anns
from ..metamodel import types, factory as f
from relationalai import debugging
from snowflake.snowpark.context import get_active_session

#--------------------------------------------------
# Globals
#--------------------------------------------------

_session = None
def get_session():
    global _session
    if not _session:
        try:
            _session = get_active_session()
        except Exception:
            from relationalai.clients.snowflake import Resources
            # TODO: we need a better way to handle global config
            _session = Resources(None, Config(), None).get_sf_session()
    return _session

#--------------------------------------------------
# Snowflake sources
#--------------------------------------------------

SFTypes = {
    "TEXT": "String",
    "FIXED": "Number",
    "FLOAT": "Float",
}

def parse_fqn(fqn:str):
    database, schema, table = fqn.split(".")
    return database, schema, table

SF_ID_REGEX = re.compile(r'^[A-Za-z_][A-Za-z0-9_$]*$')
def quoted(ident:str):
    if SF_ID_REGEX.match(ident) or ident[0] == '"':
        return ident
    return f'"{ident}"'

@dataclass
class TableInfo:
    source:Table|None
    fields:list[b.Field]
    raw_columns:list[dict]

class SchemaInfo:
    def __init__(self, database:str, schema:str) -> None:
        self.database = database
        self.schema = schema
        self.tables = defaultdict(lambda: TableInfo(None, [], []))
        self.fetched = False

    def fetch(self):
        self.fetched = True
        session = get_session()
        table_names = self.tables.keys()
        name_lookup = {x.upper(): x for x in table_names}
        tables = ", ".join([f"'{x.upper()}', '{x}'" for x in self.tables.keys()])
        query = textwrap.dedent(f"""
            begin
                SHOW COLUMNS IN SCHEMA {quoted(self.database)}.{quoted(self.schema)};
                let r resultset := (select "table_name", "column_name", "data_type" from table(result_scan(-1)) as t
                                    where "table_name" in ({tables}));
                return table(r);
            end;
        """)
        with debugging.span("fetch_schema", sql=query):
            columns = session.sql(query).collect()
        for row in columns:
            table_name, column_name, data_type = row
            table_name = name_lookup.get(table_name, table_name)
            info = self.tables[table_name]
            type_str = SFTypes[json.loads(data_type).get("type")]
            info.fields.append(b.Field(name=column_name, type_str=type_str, is_many=False))
            info.raw_columns.append(row.as_dict())

class Table():
    _schemas:dict[tuple[str, str], SchemaInfo] = {}
    _used_sources:OrderedSet[Table] = ordered_set()

    def __init__(self, fqn:str) -> None:
        self._fqn = fqn
        self._database, self._schema, self._table = parse_fqn(fqn)
        self._inited = False
        self._ref = b.Integer.ref("row_id")
        self._cols = {}
        info = self._schemas.get((self._database, self._schema))
        if not info:
            info = self._schemas[(self._database, self._schema)] = SchemaInfo(self._database, self._schema)
        info.tables[self._table].source = self

    def _lazy_init(self):
        if self._inited:
            return
        self._inited = True
        schema_info = self._schemas[(self._database, self._schema)]
        if not schema_info.fetched:
            schema_info.fetch()
        table_info = schema_info.tables[self._table]
        self._rel = b.Relationship(self._fqn, fields=[b.Field("METADATA$ROW_ID", "Number", False)] + table_info.fields)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name.lower() not in self._cols:
            self._cols[name.lower()] = Column(self, name)
        return self._cols[name.lower()]

    def into(self, concept:b.Concept, keys:list[Column]=[]):
        self._lazy_init()
        if not keys:
            keys = [getattr(self, self._rel._fields[0].name)]

        key_dict = {sanitize_identifier(k._column_name.lower()): k for k in keys}
        # TODO: this is correct, but the rel backend does the wrong thing with it
        # me = concept.new(**key_dict)
        # items = [me]
        # for field in self._rel._fields[1:]:
        #     field_rel = getattr(concept, field.name.lower())
        #     if sanitize_identifier(field.name.lower()) not in key_dict:
        #         items.append(field_rel(me, getattr(self, field.name)))
        # b.where(me).define(*items)

        # this is much less efficient than above
        me = concept.new(**key_dict)
        b.define(me)
        for field in self._rel._fields[1:]:
            if sanitize_identifier(field.name.lower()) not in key_dict:
                update = getattr(concept, field.name.lower())(me, getattr(self, field.name))
                b.define(update)

    def _compile_lookup(self, compiler:b.Compiler, ctx:b.CompilerContext):
        self._lazy_init()
        Table._used_sources.add(self)
        return

class Column(b.Producer):
    def __init__(self, source:Table, column_name:str) -> None:
        super().__init__(None)
        self._column_name = column_name
        self._source = source

        # we initialize the relationship lazily since we won't know its types
        # until we have the schema
        self._rel = None

    def _compile_lookup(self, compiler:b.Compiler, ctx:b.CompilerContext):
        compiler.lookup(self._source, ctx)
        column_name = None
        column_type = "Any"
        for field in self._source._rel._fields:
            if field.name.lower() == self._column_name.lower():
                column_name = field.name
                column_type = field.type_str
        if not column_name:
            raise ValueError(f"Column {self._column_name} not found in {self._source._fqn}")
        # if we haven't previously fixed the type for the relation after fetching
        # the schema, we need to do it now
        if not self._rel:
            safe_name = sanitize_identifier(self._source._fqn)
            self._rel = b.Relationship(safe_name, fields=[
                b.Field("symbol", "Symbol", False),
                b.Field("row_id", "Number", False),
                b.Field(column_name.lower(), column_type, False)
            ]).annotate(anns.external)

        exp = self._rel(f.literal(column_name, types.Symbol), self._source._ref, self._rel._field_refs[-1])
        return compiler.lookup(exp, ctx)