from volsite_postgres_common.db.FnT import FnT
from typing import Final
from volworld_common.api.CA import CA

from volsite_postgres_common.db.CFn import CFn

from volsite_postgres_common.fn.function import Arg, AJsonPlPgSqlFunction
from volsite_postgres_common.db.BFn import BFn

'''
    @input 
        {
            A.Data: original JSONB data
            A.Key: add attribute name
            A.Value: add attribute value
        }
    @return
        JSONB data with additional key and value or key and updated value
'''
class FnJsonbAppendKeyIntValue(AJsonPlPgSqlFunction):
    def name(self) -> str:
        return CFn.jsonb_append_key_int_value

    _src: Final[str] = "_src"
    _key: Final[str] = "_key"
    _value: Final[str] = "_value"

    def declare(self) -> list:
        return [
            Arg(self._src, FnT.JSONB),
            Arg(self._key, FnT.TEXT),
            Arg(self._value, FnT.INT),
        ]

    def out_args(self) -> list:
        return [
            Arg(Arg.result, FnT.JSONB)
        ]

    def body(self) -> str:
        return (
            f" {self._src} := ({Arg.input}->>'{CA.Data}')::{FnT.JSONB};"
            f" {self._key} := ({Arg.input}->>'{CA.Key}')::{FnT.TEXT};"
            f" {self._value} := {BFn.coalesce}(({self._src}->>{self._key})::{FnT.INT}, 0);"
            f" {self._value} := {self._value} + ({Arg.input}->>'{CA.Value}')::{FnT.INT};"
            f""
            f" {Arg.result} := {BFn.jsonb_set}({self._src}, ('{{' || {self._key} || '}}')::{FnT.TEXT_ARRAY}, "
            f"              {BFn.to_jsonb}( {self._value} ),"
            f"              true"
            f"         );"
        )
