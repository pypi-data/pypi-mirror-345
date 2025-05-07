from typing import Final

from volsite_postgres_common.db.CFn import CFn

from volsite_postgres_common.fn.function import Arg, APlPgSqlFunction
from volsite_postgres_common.db.FnT import FnT

from volworld_common.api.CA import CA
from volsite_postgres_common.db.BFn import BFn

class FnTestCurrentTime(APlPgSqlFunction):
    def name(self) -> str:
        return CFn.test_current_time

    _add_sec: Final[str] = "_add_sec"

    def declare(self) -> list:
        return [
            Arg(self._add_sec, FnT.INT),
            ]

    def in_args(self) -> list:
        return [
            Arg(Arg.input, FnT.JSONB)
        ]

    def out_args(self) -> list:
        return [
            Arg(Arg.result, FnT.TIMESTAMP)
        ]

    def body(self) -> str:
        return (
            f" if {Arg.input}->>'{CA.Second}' IS NULL THEN"
            f"  {Arg.result} := {BFn.statement_timestamp}();"
            f"  RETURN;"
            f" END IF;"
            f""
            f" {self._add_sec} := ({Arg.input}->>'{CA.Second}')::{FnT.INT};"
            f""
            f" {Arg.result} := {BFn.statement_timestamp}();"
            f" {Arg.result} := {Arg.result} + ({self._add_sec} || ' seconds')::INTERVAL;"
        )
