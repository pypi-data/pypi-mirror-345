
from volworld_common.api.CA import CA

from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.function import Arg
from deprecated import deprecated

@deprecated(version='0.1.48', reason="You should use SQL.*")
def sql__input_j_2_iid(att: str) -> str:
    return f"({Arg.input}->>'{att}')::TEXT"

@deprecated(version='0.1.48', reason="You should use SQL.*")
def sql__input_j_2_uuid(att: str) -> str:
    return f"({Arg.input}->>'{att}')::UUID"

@deprecated(version='0.1.48', reason="You should use SQL.*")
def sql__input_j_2_bint_id(att: str) -> str:
    return f"{CFn.id_2_bigint}( ({Arg.input}->>'{att}')::TEXT )"


@deprecated(version='0.1.48', reason="You should use SQL.*")
def sql__input_j_2_int_id(att: str) -> str:
    return f"{CFn.id_2_int}( ({Arg.input}->>'{att}')::TEXT )"


@deprecated(version='0.1.48', reason="You should use SQL.*")
def sql__2_id(*att: str) -> str:
    return f"{CFn.bigint_2_id}({'.'.join(att)})"


@deprecated(version='0.1.48', reason="You should use SQL._2_bint")
def sql__2_bint(*att: str) -> str:
    return f"{CFn.id_2_bigint}({'.'.join(att)})"


@deprecated(version='0.1.48', reason="You should use SQL.order_by_cols")
def sql__order_by_cols(col_dict: dict, def_col: str) -> str:
    res = f"CASE ({Arg.input}->>'{CA.SortBy}')::TEXT"
    for arg in col_dict.keys():
        res = f"{res}\n          WHEN '{arg}' THEN {col_dict[arg]}"
    res = f"{res}\n          ELSE {def_col}"  # ELSE NULL
    res = f"{res}\nEND"
    return res


@deprecated(version='0.1.48', reason="You should use SQL.order_by")
def sql__order_by(col_dict: dict, def_col: str) -> str:
    return (
        f" CASE WHEN ({Arg.input}->>'{CA.SortDirection}')::TEXT = '{CA.Ascending}' THEN "
        f"      {sql__order_by_cols(col_dict, def_col)}"
        f" ELSE"
        f"      NULL"
        f" END"
        f" {CA.Ascending},"
        f""
        f" CASE WHEN ({Arg.input}->>'{CA.SortDirection}')::TEXT = '{CA.Descending}' THEN "
        f"      {sql__order_by_cols(col_dict, def_col)}"
        f" ELSE"
        f"      NULL"
        f" END"
        f" {CA.Descending}"
    )

class SQL:

    @staticmethod
    def input_2_iid(att: str) -> str:
        return f"({Arg.input}->>'{att}')::TEXT"

    @staticmethod
    def input_2_uuid(att: str) -> str:
        return f"({Arg.input}->>'{att}')::UUID"

    @staticmethod
    def input_2_bigint(att: str) -> str:
        return f"({Arg.input}->>'{att}')::BIGINT"

    @staticmethod
    def input_2_int(att: str) -> str:
        return f"({Arg.input}->>'{att}')::INT"

    @staticmethod
    def input_iid_2_bint(att: str) -> str:
        return SQL.input_iid_2_bigint(att)

    @staticmethod
    def input_iid_2_bigint(att: str) -> str:
        return f"{CFn.id_2_bigint}( ({Arg.input}->>'{att}')::TEXT )"

    @staticmethod
    def input_iid_2_int(att: str) -> str:
        return f"{CFn.id_2_int}( ({Arg.input}->>'{att}')::TEXT )"

    @staticmethod
    def bint_2_iid(*att: str) -> str:
        return f"{CFn.bigint_2_id}({'.'.join(att)})"

    @staticmethod
    def int_2_iid(*att: str) -> str:
        return f"{CFn.int_2_id}({'.'.join(att)})"

    @staticmethod
    def iid_2_bint(*att: str) -> str:
        return f"{CFn.id_2_bigint}({'.'.join(att)})"
    @staticmethod
    def jsonb_agg_or_empty(*att: str) -> str:
        return f"{BFn.coalesce}( {BFn.jsonb_agg} ({'.'.join(att)}), '[]'::jsonb )"

    @staticmethod
    def jsonb_object_agg_or_empty(key: str, value: str) -> str:
        return f"{BFn.coalesce}( {BFn.jsonb_object_agg} ({key}, {value}), '{{}}'::jsonb )"

    @staticmethod
    def order_by(col_dict: dict, def_col: str) -> str:
        return (
            f" CASE WHEN ({Arg.input}->>'{CA.SortDirection}')::TEXT = '{CA.Ascending}' THEN "
            f"      {SQL.order_by_cols(col_dict, def_col)}"
            f" ELSE"
            f"      NULL"
            f" END"
            f" {CA.Ascending},"
            f""
            f" CASE WHEN ({Arg.input}->>'{CA.SortDirection}')::TEXT = '{CA.Descending}' THEN "
            f"      {SQL.order_by_cols(col_dict, def_col)}"
            f" ELSE"
            f"      NULL"
            f" END"
            f" {CA.Descending}"
        )

    @staticmethod
    def order_by_cols(col_dict: dict, def_col: str) -> str:
        res = f"CASE ({Arg.input}->>'{CA.SortBy}')::TEXT"
        for arg in col_dict.keys():
            res = f"{res}\n          WHEN '{arg}' THEN {col_dict[arg]}"
        res = f"{res}\n          ELSE {def_col}"  # ELSE NULL
        res = f"{res}\nEND"
        return res