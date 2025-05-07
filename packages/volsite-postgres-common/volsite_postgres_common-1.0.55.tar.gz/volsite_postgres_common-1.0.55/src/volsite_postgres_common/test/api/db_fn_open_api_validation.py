from volsite_postgres_common.fn.json import json_fn_db
from volsite_postgres_common.test.db.TestDb import TestDb
from volworld_common.test.Timer import Timer
from api.A import A
from volsite_postgres_common.test.db.db_response_util import response_to_dict
from volsite_postgres_common.test.api.OpenApiValidation import OpenApiValidation


def db_fn_open_api_validation(fn: str, req, res, attList):
    fn_path = f"/{fn}"
    val = OpenApiValidation()
    val.validate_POST_request(req, fn_path, attList)

    if A.___Error___ not in res:
        val.validate_POST_response({
            A.Data: res[A.Data]
        }, fn_path, res[A.HttpStatus], attList)
    else:
        val.validate_POST_response({
            A.___Error___: res[A.___Error___]
        }, fn_path, res[A.HttpStatus], attList)


def json_fn_db_with_validation(
        fn: str, req: dict,
        test_db: TestDb, attList,
        do_commit: bool = False,
        print_long_att: bool = True):
    with Timer(f"Call DB Function [{fn}]"):
        resp = json_fn_db(fn, req, test_db, attList, do_commit=do_commit, print_long_att=print_long_att)
    print('req = ', req)
    print('resp = ', resp)
    db_fn_open_api_validation(fn, req, resp, attList)
    return response_to_dict(resp)
