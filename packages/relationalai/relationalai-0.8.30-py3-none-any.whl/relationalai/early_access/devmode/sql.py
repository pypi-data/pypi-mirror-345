"""
A simple metamodel for SQL.
"""
from __future__ import annotations
from dataclasses import dataclass
from io import StringIO
import rich
from typing import Any, IO, Optional, Tuple, Union


@dataclass(frozen=True)
class Node:
    def __str__(self):
        return to_string(self)

#-------------------------------------------------
# Table
#-------------------------------------------------

@dataclass(frozen=True)
class Column(Node):
    name: str
    type: str

@dataclass(frozen=True)
class Table(Node):
    name: str
    columns: list[Column]

#-------------------------------------------------
# Statements
#-------------------------------------------------

@dataclass(frozen=True)
class CreateTable(Node):
    table: Table

@dataclass(frozen=True)
class CreateView(Node):
    name: str
    query: Union[Select, CTE]

@dataclass(frozen=True)
class Insert(Node):
    table: str
    columns: list[str]
    values: list[Tuple[Any, ...]]
    select: Optional[Select]

@dataclass(frozen=True)
class Update(Node):
    table: str
    set: list[UpdateSet]
    where: Optional[Where]

@dataclass(frozen=True)
class UpdateSet(Node):
    name: str
    expression: str

@dataclass(frozen=True)
class Select(Node):
    distinct: bool
    vars: list[VarRef]
    froms: list[From]
    where: Optional[Where]

@dataclass(frozen=True)
class VarRef(Node):
    name: str
    column: Optional[str]
    alias: Optional[str]

@dataclass(frozen=True)
class From(Node):
    table: str
    alias: Optional[str]

# TODO: consider removing Where and make Select.where: Expr
@dataclass(frozen=True)
class Where(Node):
    expression: Expr

#-------------------------------------------------
# Clauses
#-------------------------------------------------
# TODO: move clauses from other sections

@dataclass(frozen=True)
class CTE(Node):
    """ Common Table Expressions. """
    recursive: bool
    name: str
    columns: list[str]
    selects: list[Select]

#-------------------------------------------------
# Expressions
#-------------------------------------------------

@dataclass(frozen=True)
class Expr(Node):
    pass

@dataclass(frozen=True)
class And(Expr):
    expr: list[Expr]

@dataclass(frozen=True)
class Or(Expr):
    expr: list[Expr]

@dataclass(frozen=True)
class Terminal(Expr):
    """ Avoid going deeper in the meta-model, this is an arbitrary terminal expression."""
    expr: str


#--------------------------------------------------
# Printer
#--------------------------------------------------

def to_string(node, inlined=False) -> str:
    io = StringIO()
    pprint(node, io = io, inlined = inlined)
    return io.getvalue()

def pprint(node:Node, io: Optional[IO[str]] = None, inlined = False) -> None:
    # Table
    if isinstance(node, Table):
        rich_print(io, f"TABLE {node.name} (")
        rich_print(io, ', '.join([str(c) for c in node.columns]))
        rich_print(io, ")")
    elif isinstance(node, Column):
        rich_print(io, f"{node.name} {node.type}")

    # Statements
    elif isinstance(node, CreateTable):
        rich_print(io, f"CREATE {node.table};")
    elif isinstance(node, CreateView):
        # TODO - crying a bit inside :(
        rich_print(io, f"DROP TABLE IF EXISTS {node.name};\n")
        rich_print(io, f"CREATE VIEW {node.name} AS ")
        pprint(node.query, io, True)
        rich_print(io, ";")
    elif isinstance(node, Insert):
        rich_print(io, f"INSERT INTO {node.table} ")
        if len(node.columns) > 0:
            rich_print(io, "(")
            rich_print(io, ', '.join([str(s) for s in node.columns]))
            rich_print(io, ") ")
        if len(node.values) > 0:
            rich_print(io, "VALUES (")
            rich_print(io, ', '.join([str(s) for s in node.values]))
            rich_print(io, ")")
        if node.select is not None:
            pprint(node.select, io, True)
        rich_print(io, ";")
    elif isinstance(node, Update):
        rich_print(io, f"UPDATE {node.table} SET ")
        rich_print(io, ', '.join([str(s) for s in node.set]))
        if node.where is not None:
            pprint(node.where, io)
        rich_print(io, ";")
    elif isinstance(node, UpdateSet):
        rich_print(io, f"{node.name} = {node.expression}")
    elif isinstance(node, Select):
        rich_print(io, "SELECT ")
        if node.distinct:
            rich_print(io, "DISTINCT ")
        rich_print(io, ', '.join([str(v) for v in node.vars]))
        rich_print(io, " FROM ")
        rich_print(io, ', '.join([str(v) for v in node.froms]))
        if node.where:
            pprint(node.where, io)
        if not inlined:
            rich_print(io, ";")
    elif isinstance(node, VarRef):
        if node.column is None:
            rich_print(io, node.name)
        else:
            rich_print(io, f"{node.name}.{node.column}")
        if node.alias and node.alias != node.column:
            rich_print(io, f" as {node.alias}")
    elif isinstance(node, From):
        rich_print(io, node.table)
        if node.alias is not None:
            rich_print(io, f" AS {node.alias}")
    elif isinstance(node, Where):
        rich_print(io, f" WHERE {node.expression}")

    # Clauses
    elif isinstance(node, CTE):
        rich_print(io, "WITH ")
        if node.recursive:
            rich_print(io, "RECURSIVE ")
        rich_print(io, f"{node.name} ({', '.join(node.columns)}) AS (\n  ")
        for i, s in enumerate(node.selects):
            if i != 0:
                rich_print(io, "\n    UNION ALL\n  ")
            pprint(s, io, True)

        rich_print(io, f"\n) SELECT * FROM {node.name}")
        if not inlined:
            rich_print(io, ";")

    # Expressions
    elif isinstance(node, And):
        rich_print(io, ' AND '.join([str(c) for c in node.expr]))
    elif isinstance(node, Or):
        rich_print(io, ' OR '.join([str(c) for c in node.expr]))
    elif isinstance(node, Terminal):
        rich_print(io, node.expr)
    else:
        raise Exception(f"Missing SQL.pprint({type(node)}): {node}")

def rich_print(io, args):
    rich.print(args, file=io, end='')
