from volworld_common.api.CA import CA

from volsite_postgres_common.db.CFn import CFn

from volsite_postgres_common.fn.function import Arg, AJsonPlPgSqlFunction
from volsite_postgres_common.db.BFn import BFn

class FnJsonbArray2IdDict(AJsonPlPgSqlFunction):
    def name(self) -> str:
        return CFn.jsonb_array_2_id_array_dict


    def declare(self) -> list:
        return [
        ]

    # @ref by ChatGPT
    def body(self) -> str:
        return (
            f"{Arg.result} := {BFn.jsonb_object_agg}(dd.{CA.Id}, dd.data_array) "
            f"       FROM ( "
            f"          SELECT {CA.Id}, {BFn.jsonb_agg}({CA.Data}) as data_array"
            f"          FROM ("
            f"          SELECT"
            f"               e.element->>'{CA.Id}' AS {CA.Id},"
            f"               jsonb_strip_nulls(e.element - '{CA.Id}') AS {CA.Data}"
            f"          FROM ("
            f"             SELECT {BFn.jsonb_array_elements}({Arg.input}) AS element"
            f"          ) e"
            f"       ) d GROUP BY d.{CA.Id}"
            f"      ) dd;"
            f"{Arg.result} := {BFn.coalesce}({Arg.result}, '{{}}'::JSONB);"
        )
