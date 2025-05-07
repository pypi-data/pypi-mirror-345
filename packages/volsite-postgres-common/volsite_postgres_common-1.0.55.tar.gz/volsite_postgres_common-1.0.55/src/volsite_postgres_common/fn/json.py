from psycopg2._json import Json
from typing import Final
import json
from volworld_common.api.CA import CA
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volworld_common.test.Timer import Timer

from volsite_postgres_common.fn.FnJsonbAppendKeyIntValue import FnJsonbAppendKeyIntValue
from volsite_postgres_common.fn.FnJsonbArray2IdArrayDict import FnJsonbArray2IdDict
from volsite_postgres_common.fn.FnJsonbArray2IdObjectDict import FnJsonbArray2IdObjectDict
from volsite_postgres_common.fn.FnJsonbErrorCodeResult import FnJsonbErrorCodeResult
from volsite_postgres_common.fn.FnTestCurrentTime import FnTestCurrentTime
from volsite_postgres_common.test.db.TestDb import TestDb
from volworld_common.util.json import print_json_by_attributes


def json_fn(fn: str, input_j: dict, conn, attList,
            do_commit: bool = False,
            print_input_output: bool = True,
            print_long_att: bool = True):  # -> dict:
    cursor = conn.cursor()
    if print_input_output:
        print(f'==== [FN] {fn} ====')
        print('=== Input ===')
        print('<code>')
        print_json_by_attributes(input_j, attList, print_long_att)
        print('</code>')
    cursor.execute(f'SELECT {fn}( %s::JSONB ) AS {CA.Result}', (
        Json(input_j),
    ))
    rows = cursor.fetchall()
    assert 1 == len(rows)
    # print('[json_fn] rows[0] = %r' % rows[0])
    if do_commit:
        conn.commit()
    output = rows[0][CA.Result]
    if print_input_output:
        print('=== Output ===')
        print('<code>')
        print_json_by_attributes(output, attList, print_long_att)
        print('</code>')
    return output

# def convert_json_by_attributes(j, attList) -> str:
#     abb_att = {}
#
#     for a in attList:
#         for name in a.__dict__:
#             abb = a.__dict__[name]
#             abb_att[f"\"{abb}\":"] = f"\"{abb}__{name}\":"
#
#     res = json.dumps(j, indent=4, sort_keys=True)
#     for att in abb_att.keys():
#         res = res.replace(att, abb_att[att])
#
#     return res

# def print_json_by_attributes(j, attList, print_long_att: bool = False):
#     if not print_long_att:
#         print(json.dumps(j, indent=4, sort_keys=True))
#         return
#
#     print(convert_json_by_attributes(j, attList))


def json_fn_db(
        fn: str, input_j: dict,
        test_db: TestDb, attList,
        do_commit: bool = False,
        print_long_att: bool = True):  # -> dict:
    with Timer(fn):
        return json_fn(fn, input_j, test_db.p_conn, attList,
                       do_commit=do_commit,
                       print_input_output=test_db.print_input_output,
                       print_long_att=print_long_att)


fn_jsonb_array_2_int_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_int_array} (JSONB) "
    f" RETURNS INT[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::INT[] || ARRAY[]::INT[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_array_2_smallint_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_smallint_array} (JSONB) "
    f" RETURNS SMALLINT[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::SMALLINT[] || ARRAY[]::SMALLINT[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_array_2_bigint_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_bigint_array} (JSONB) "
    f" RETURNS BIGINT[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::BIGINT[] || ARRAY[]::BIGINT[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_array_2_text_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_text_array} (JSONB) "
    f" RETURNS TEXT[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::TEXT[] || ARRAY[]::TEXT[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

jsonb_array_2_lower_text_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_lower_text_array} (JSONB) "
    f" RETURNS TEXT[] "
    f" AS $$ "
    f"   SELECT array_agg({BFn.lower}({BFn.trim}(x)))::TEXT[] || ARRAY[]::TEXT[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "

    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_array_2_uuid_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_array_2_uuid_array} (JSONB) "
    f" RETURNS UUID[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::UUID[] || ARRAY[]::UUID[] FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_2_jsonb_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_2_jsonb_array} (JSONB) "
    f" RETURNS JSONB[] "
    f" AS $$ "
    f"   SELECT array_agg(x)::JSONB[] || ARRAY[]::JSONB[] FROM {BFn.jsonb_array_elements}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_jsonb_remove_key: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_remove_key} (JSONB, TEXT) "
    f" RETURNS JSONB "
    f" AS $$ "
    f"   SELECT $1 - $2;"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

# @ref https://stackoverflow.com/questions/36171737/how-to-count-setof-number-of-keys-of-json-in-postgresql
fn_count_jsonb_keys: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.count_jsonb_keys} (JSONB) "
    f" RETURNS BIGINT "
    f" AS $$ "
    f"   SELECT COUNT(*) FROM (SELECT {BFn.jsonb_object_keys}($1)) v;"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")


'''

fn_jsonb_add_key_value: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {Fn.jsonb_add_key_value} (JSONB, JSONB) "
    f" RETURNS JSONB "
    f" AS $$ "
    f"   SELECT $1 || $2;"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")
'''

# @ref https://stackoverflow.com/questions/47064098/postgresql-add-object-to-jsonb-array-by-function
fn_jsonb_add_key_val_elements: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_add_key_value_elements} (_arr JSONB, _val JSONB) "
    f" RETURNS JSONB "
    f" AS $$ "
    f"   SELECT jsonb_agg(elem || _val)"
    f"      FROM jsonb_array_elements(_arr) elem"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

fn_sort_jsonb_array_multi: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.sort_jsonb_array_multi} ("
    f"      input_jsonb JSONB, "
    f"      sort_key1 TEXT, sort_order1 TEXT, "
    f"      sort_key2 TEXT DEFAULT NULL, sort_order2 TEXT DEFAULT 'ASC') "
    f" RETURNS JSONB "
    f" AS"
    f" $$"
    f"   BEGIN"
    f"      RETURN ("
    f"          SELECT jsonb_agg(elem ORDER BY "
    f"              CASE WHEN sort_order1 = 'ASC' THEN elem ->> sort_key1 ELSE NULL END ASC,"
    f"              CASE WHEN sort_order1 = 'DESC' THEN elem ->> sort_key1 ELSE NULL END DESC,"
    f"              CASE WHEN sort_order2 = 'ASC' THEN elem ->> sort_key2 ELSE NULL END ASC,"
    f"              CASE WHEN sort_order2 = 'DESC' THEN elem ->> sort_key2 ELSE NULL END DESC"
    f"              )"
    f"          FROM jsonb_array_elements(input_jsonb) AS elem"
    f"      );"
    f"  END;"
    f" $$ "
    f" LANGUAGE plpgsql "
    f" IMMUTABLE;")

def insert_util_fn__json(conn):
    cursor = conn.cursor()
    cursor.execute(fn_jsonb_array_2_bigint_array)
    cursor.execute(fn_jsonb_array_2_int_array)
    cursor.execute(fn_jsonb_array_2_smallint_array)
    cursor.execute(fn_jsonb_array_2_text_array)
    cursor.execute(jsonb_array_2_lower_text_array)
    cursor.execute(fn_jsonb_array_2_uuid_array)
    cursor.execute(fn_jsonb_2_jsonb_array)
    cursor.execute(fn_jsonb_remove_key)
    cursor.execute(fn_count_jsonb_keys)
    # cursor.execute(fn_jsonb_add_key_value)
    cursor.execute(fn_jsonb_add_key_val_elements)
    cursor.execute(fn_sort_jsonb_array_multi)

    cursor.execute(FnJsonbArray2IdDict().build_function())
    cursor.execute(FnJsonbArray2IdObjectDict().build_function())
    cursor.execute(FnJsonbAppendKeyIntValue().build_function())
    cursor.execute(FnJsonbErrorCodeResult().build_function())
    cursor.execute(FnTestCurrentTime().build_function())

    conn.commit()
