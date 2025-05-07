from __future__ import annotations
import atexit
from collections import defaultdict
import re
import textwrap

from pandas import DataFrame
from typing import Any
import relationalai as rai

from relationalai import debugging
from relationalai.clients import result_helpers
from relationalai.early_access.metamodel import ir, executor as e, factory as f
from relationalai.early_access.rel import Compiler
from relationalai.clients.config import Config

class RelExecutor(e.Executor):
    """Executes Rel code using the RAI client."""

    def __init__(self, database: str, dry_run: bool = False, keep_model: bool = True, config:Config|None=None) -> None:
        super().__init__()
        self.database = database
        self.dry_run = dry_run
        self.keep_model = keep_model
        self.compiler = Compiler()
        self.config = config or Config()
        self._resources = None
        self._last_model = None
        self._last_sources_version = (-1, None)

    @property
    def resources(self):
        if not self._resources:
            with debugging.span("create_session"):
                self.dry_run |= bool(self.config.get("compiler.dry_run", False))
                self._resources = rai.clients.snowflake.Resources(dry_run=self.dry_run)
                if not self.dry_run:
                    self.engine = self._resources.get_default_engine_name()
                    if not self.keep_model:
                        atexit.register(self._resources.delete_graph, self.database, True)
        return self._resources

    def check_graph_index(self):
        # Has to happen first, so self.dry_run is populated.
        resources = self.resources

        if self.dry_run:
            return

        from relationalai.early_access.builder.snowflake import Table
        table_sources = Table._used_sources
        if not table_sources.has_changed(self._last_sources_version):
            return

        model = self.database
        app_name = resources.get_app_name()
        engine_name = self.engine

        program_span_id = debugging.get_program_span_id()
        sources = [t._fqn for t in Table._used_sources]
        self._last_sources_version = Table._used_sources.version()

        assert self.engine is not None

        with debugging.span("poll_use_index", sources=sources, model=model, engine=engine_name):
            resources.poll_use_index(app_name, sources, model, self.engine, program_span_id)

    def report_errors(self, problems: list[dict[str, Any]], abort_on_error=True):
        from relationalai import errors
        all_errors = []
        undefineds = []
        pyrel_errors = defaultdict(list)
        pyrel_warnings = defaultdict(list)

        for problem in problems:
            message = problem.get("message", "")
            report = problem.get("report", "")
            # TODO: we need to build source maps
            # path = problem.get("path", "")
            # source_task = self._install_batch.line_to_task(path, problem["start_line"]) or task
            # source = debugging.get_source(source_task) or debugging.SourceInfo()
            source = debugging.SourceInfo()
            severity = problem.get("severity", "warning")
            code = problem.get("code")

            if severity in ["error", "exception"]:
                if code == "UNDEFINED_IDENTIFIER":
                    match = re.search(r'`(.+?)` is undefined', message)
                    if match:
                        undefineds.append((match.group(1), source))
                    else:
                        all_errors.append(errors.RelQueryError(problem, source))
                elif "overflowed" in report:
                    all_errors.append(errors.NumericOverflow(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_errors[problem["props"]["pyrel_id"]].append(problem)
                elif abort_on_error:
                    all_errors.append(errors.RelQueryError(problem, source))
            else:
                if code == "ARITY_MISMATCH":
                    errors.ArityMismatch(problem, source)
                elif code == "IC_VIOLATION":
                    all_errors.append(errors.IntegrityConstraintViolation(problem, source))
                elif code == "PYREL_ERROR":
                    pyrel_warnings[problem["props"]["pyrel_id"]].append(problem)
                else:
                    errors.RelQueryWarning(problem, source)

        if abort_on_error and len(undefineds):
            all_errors.append(errors.UninitializedPropertyException(undefineds))

        if abort_on_error:
            for pyrel_id, pyrel_problems in pyrel_errors.items():
                all_errors.append(errors.ModelError(pyrel_problems))

        for pyrel_id, pyrel_problems in pyrel_warnings.items():
            errors.ModelWarning(pyrel_problems)


        if len(all_errors) == 1:
            raise all_errors[0]
        elif len(all_errors) > 1:
            raise errors.RAIExceptionSet(all_errors)

    def execute(self, model: ir.Model, task:ir.Task) -> DataFrame:
        self.check_graph_index()
        resources= self.resources

        rules_code = ""
        if self._last_model != model:
            with debugging.span("compile", metamodel=model) as install_span:
                base = textwrap.dedent("""
                    declare pyrel_error_attrs(err in UInt128, attr in String, v) requires true

                """)
                rules_code = base + self.compiler.compile(model)
                install_span["compile_type"] = "model"
                install_span["rel"] = rules_code
                rules_code = resources.create_models_code([("pyrel_qb_0", rules_code)])
                self._last_model = model


        with debugging.span("compile", metamodel=task) as compile_span:
            base = textwrap.dedent("""
                def output(:pyrel_error, err, attr, val):
                    pyrel_error_attrs(err, attr, val)

            """)
            task_model = f.compute_model(f.logical([task]))
            task_code = base + self.compiler.compile(task_model, {"no_declares": True})
            compile_span["compile_type"] = "query"
            compile_span["rel"] = task_code


        full_code = textwrap.dedent(f"""
            {rules_code}
            {task_code}
        """)

        if self.dry_run:
            return DataFrame()

        raw_results = resources.exec_raw(self.database, self.engine, full_code, False, nowait_durable=True)
        df, errs = result_helpers.format_results(raw_results, None)  # Pass None for task parameter
        self.report_errors(errs)

        return df
