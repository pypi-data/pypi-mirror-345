
from volsite_postgres_common.fn.AInsertFunction import AInsertFunction
from volsite_postgres_common.fn.http_status.FnHttpStatusData import FnHttpStatusData
from volsite_postgres_common.fn.http_status.FnHttpStatusError import FnHttpStatusError
from volsite_postgres_common.fn.http_status.FnHttpStatusErrorCodeOnly import FnHttpStatusErrorCodeOnly


class InsertHttpStatusFn(AInsertFunction):

    def build_functions(self) -> list:
        fn_list = [
            FnHttpStatusData(),
            FnHttpStatusError(),
            FnHttpStatusErrorCodeOnly(),
        ]

        res = list()
        for fn in fn_list:
            res.append(fn.build_function())

        return res

def insert_util_fn__http_status(conn):
    InsertHttpStatusFn().insert_functions(conn, do_commit=False)