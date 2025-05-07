from __future__ import annotations

import duckdb
from pandas import DataFrame
from typing import Any, Union

from relationalai.early_access.metamodel import ir, executor as e
from . import Compiler

class Executor(e.Executor):

    def execute(self, model: ir.Model, task:ir.Task) -> Union[DataFrame, Any]:
        c = Compiler()
        sql = c.compile(model)
        connection = duckdb.connect()
        try:
            result = connection.query(sql).to_df()
            return result
        finally:
            connection.close()
