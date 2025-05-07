import textwrap
from typing import List, Optional

from pandas import DataFrame
import relationalai as rai
from relationalai import debugging
from relationalai.clients import result_helpers
from relationalai.early_access.dsl.ir.compiler import Compiler
from relationalai.early_access.dsl.ontologies.models import Model
from relationalai.early_access.metamodel import ir
from relationalai.early_access.rel.compiler import ModelToRel


class RelExecutor:

    def __init__(self, database: str, dry_run: bool = False) -> None:
        super().__init__()
        self.database = database
        self.dry_run = dry_run
        self.compiler = Compiler()
        self.model_to_rel = ModelToRel()
        self._resources = None
        self._last_model = None

    @property
    def resources(self):
        if not self._resources:
            with debugging.span("create_session"):
                self._resources = rai.clients.snowflake.Resources()
                self._resources.config.set("use_graph_index", False)
                if not self.dry_run:
                    try:
                        if not self._resources.get_database(self.database):
                            self._resources.create_graph(self.database)
                    except Exception as e:
                        if "already exists" not in str(e).lower():
                            raise e
                    self.engine = self._resources.config.get("engine", strict=False)
                    if not self.engine:
                        self.engine = self._resources.get_default_engine_name()
        return self._resources

    def execute_model(self, model: Model, result_cols: Optional[List[str]] = None) -> DataFrame:
        ir_model = self.compiler.compile_model(model)
        query_ir_model = self.compiler.compile_queries(model.queries())
        return self.execute(ir_model, query_ir_model, result_cols)

    def execute(self, model: ir.Model, query: ir.Model, result_cols: Optional[List[str]] = None) -> DataFrame:
        resources = self.resources

        rules_code = ""
        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as install_span:
                rules_code = str(self.model_to_rel.to_rel(model))
                install_span["compile_type"] = "model"
                install_span["rel"] = rules_code
                rules_code = resources.create_models_code([("pyrel_qb_0", rules_code)])
                self._last_model = model

        with debugging.span("compile", metamodel=query) as compile_span:
            query_code = str(self.model_to_rel.to_rel(query, options={"no_declares": True}))
            compile_span["compile_type"] = "query"
            compile_span["rel"] = query_code

        full_code = textwrap.dedent(f"""
            {rules_code}
            {query_code}
        """)

        if self.dry_run:
            return DataFrame()

        raw_results = self.resources.exec_raw(self.database, self.engine, full_code, False, nowait_durable=True)
        df, _ = result_helpers.format_results(raw_results, None, result_cols)  # Pass None for task parameter
        return df