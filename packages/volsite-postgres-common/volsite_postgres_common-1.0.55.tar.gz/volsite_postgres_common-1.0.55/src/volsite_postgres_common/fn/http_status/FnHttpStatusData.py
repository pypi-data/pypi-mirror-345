from volworld_common.api.CA import CA
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.function import AJsonPlPgSqlFunction, Arg

class FnHttpStatusData(AJsonPlPgSqlFunction):

    def name(self) -> str:
        return CFn.http_status_data

    '''
    [CA.HttpStatus]: SMALLINT
    [CA.Data]: JSONB
    '''
    def body(self) -> str:
        return (
            f" {Arg.result} := {BFn.jsonb_build_object}("
            f"    '{CA.HttpStatus}', ({Arg.input}->>'{CA.HttpStatus}')::SMALLINT, "
            f"          '{CA.Data}', ({Arg.input}->>'{CA.Data}')::JSONB"  
            f" );"
        )