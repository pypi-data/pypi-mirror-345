from typing import Final
from volsite_postgres_common.db.FnT import FnT
from volworld_common.api.CA import CA

from volsite_postgres_common.db.CFn import CFn

from volsite_postgres_common.fn.function import Arg, AJsonPlPgSqlFunction
from volsite_postgres_common.db.BFn import BFn

class FnJsonbErrorCodeResult(AJsonPlPgSqlFunction):
    def name(self) -> str:
        return CFn.jsonb_error_code_result


    _http_code: Final[str] = "_http_code"
    _error_code: Final[str] = "_error_code"

    def in_args(self) -> list:
        return [
            Arg(self._http_code, FnT.INT),
            Arg(self._error_code, FnT.INT)
        ]

    def out_args(self) -> list:
        return [
            Arg(Arg.result, FnT.JSONB)
        ]

    def body(self) -> str:
        return (
            f" {Arg.result} := {BFn.jsonb_build_object}("
            f"      '{CA.HttpStatus}', {self._http_code},"
            f"      '{CA.___Error___}', {BFn.jsonb_build_object}("
            f"            '{CA.Code}', {self._error_code}"
            f"          )"
            f"      );"
        )
