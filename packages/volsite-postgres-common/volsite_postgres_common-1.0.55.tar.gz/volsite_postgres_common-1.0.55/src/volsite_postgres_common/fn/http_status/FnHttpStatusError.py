from volworld_common.api.CA import CA
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.function import AJsonPlPgSqlFunction, Arg


class FnHttpStatusError(AJsonPlPgSqlFunction):

    def name(self) -> str:
        return CFn.http_status_error

    '''
    [CA.HttpStatus]: SMALLINT
    [CA.___Error___]: JSONB
    '''
    def body(self) -> str:
        return (
            f" {Arg.result} := {BFn.jsonb_build_object}("
            f"     '{CA.HttpStatus}', ({Arg.input}->>'{CA.HttpStatus}')::SMALLINT, "
            f"    '{CA.___Error___}', ({Arg.input}->>'{CA.___Error___}')::JSONB"  
            f" );"
        )