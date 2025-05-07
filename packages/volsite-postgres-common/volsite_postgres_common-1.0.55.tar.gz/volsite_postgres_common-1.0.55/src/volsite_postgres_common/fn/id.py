from typing import Final

from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.insert import insert_function

ID_PREFIX: Final = 'i'
ENUM_PREFIX: Final = 'e'


bigint_2_id: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.bigint_2_id} (_bid BIGINT) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT CONCAT ( '{ID_PREFIX}', _bid)"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

int_2_id: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.int_2_id} (_bid INT) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT CONCAT ( '{ID_PREFIX}', _bid)"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")


id_2_bigint: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.id_2_bigint} (_bid TEXT) "
    f" RETURNS BIGINT "
    f" AS"
    f" $$"
    f"   SELECT CAST((SPLIT_PART ( _bid, '{ID_PREFIX}', '2')) AS BIGINT)"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")


id_2_int: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.id_2_int} (_bid TEXT) "
    f" RETURNS INT "
    f" AS"
    f" $$"
    f"   SELECT CAST((SPLIT_PART ( _bid, '{ID_PREFIX}', '2')) AS INT)"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

jsonb_id_array_2_bigint_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_id_array_2_bigint_array} (JSONB) "
    f" RETURNS BIGINT[] "
    f" AS $$ "
    f"   SELECT array_agg({CFn.id_2_bigint}(x))::BIGINT[] || ARRAY[]::BIGINT[] "
    f"      FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

jsonb_id_array_2_int_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.jsonb_id_array_2_int_array} (JSONB) "
    f" RETURNS INT[] "
    f" AS $$ "
    f"   SELECT array_agg({CFn.id_2_int}(x))::INT[] || ARRAY[]::INT[] "
    f"      FROM {BFn.jsonb_array_elements_text}($1) t(x);"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")


bigint_array_2_id_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.bigint_array_2_id_array} ("
    f" IN _input BIGINT[], "
    f" OUT _result TEXT[]"
    f" ) "
    f" AS"
    f" $$"
    f" DECLARE"
    f"   _text_id   BIGINT;"
    f" BEGIN "
    f"  _result := ARRAY[]::TEXT[];"
    f"  IF _input IS NULL THEN"
    f"      RETURN;"
    f"  END IF;"
    f""
    f" FOREACH _text_id IN ARRAY _input "
    f" LOOP "
    f"   _result := _result || {CFn.bigint_2_id}(_text_id); "
    f" END LOOP;"
    f""
    f" END;"
    f" $$ "
    f" LANGUAGE PlPgSql "
    f" ;")

def insert_util_fn__id(conn):
    insert_function(bigint_2_id, CFn.bigint_2_id, conn)
    insert_function(int_2_id, CFn.int_2_id, conn)
    insert_function(id_2_bigint, CFn.id_2_bigint, conn)
    insert_function(id_2_int, CFn.id_2_int, conn)

    insert_function(bigint_array_2_id_array, CFn.bigint_array_2_id_array, conn)

    insert_function(jsonb_id_array_2_bigint_array, CFn.jsonb_id_array_2_bigint_array, conn)
    insert_function(jsonb_id_array_2_int_array, CFn.jsonb_id_array_2_int_array, conn)
