from typing import Final
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.insert import insert_function


# @ref https://stackoverflow.com/questions/39900397/check-if-anyelement-isnull-postgresql
is_null: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.is_null} (anyelement) "
    f" RETURNS BOOLEAN "
    f" AS"
    f" $$"
    f"   SELECT $1 IS NULL"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

# @ref https://stackoverflow.com/questions/2913368/sorting-array-elements
array_sort: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.array_sort} (ANYARRAY) "
    f" RETURNS ANYARRAY "
    f" AS"
    f" $$"
    f"   SELECT ARRAY(SELECT unnest($1) ORDER BY 1)"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

# @ref https://stackoverflow.com/questions/3994556/eliminate-duplicate-array-values-in-postgres
array_sort_unique: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.array_sort_unique} (ANYARRAY) "
    f" RETURNS ANYARRAY "
    f" AS"
    f" $$"
    f"   SELECT ARRAY( "
    f"     SELECT DISTINCT $1[s.i]  "
    f"     FROM generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)  "
    f"     ORDER BY 1  "
    f"               );"
    f" $$ "
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

is_text_in_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.is_text_in_array} (    "
    f"      search_text text, "
    f"      text_array text[]) "
    f" RETURNS BOOLEAN "
    f" AS"
    f" $$"
    f" DECLARE"
    f"  found boolean;"
    f" BEGIN"
    f"   SELECT search_text = ANY(text_array) INTO found; "
    f"   RETURN found;"
    f" END;"
    f" $$ "
    f" LANGUAGE PlPgSQL "
    f" IMMUTABLE;")


if_null_2_empty_bigint_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.if_null_2_empty_bigint_array} ("
    f" IN _input BIGINT[], "
    f" OUT _result BIGINT[]"
    f" ) "
    f" AS"
    f" $$"
    f" BEGIN "
    f"  IF _input IS NULL THEN"
    f"      _result := ARRAY[]::BIGINT[];"
    f"      RETURN;"
    f"  END IF;"
    f"  _result := _input;"
    f" END;"
    f" $$ "
    f" LANGUAGE PlPgSql "
    f" ;")

if_null_2_empty_uuid_array: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.if_null_2_empty_uuid_array} ("
    f" IN _input UUID[], "
    f" OUT _result UUID[]"
    f" ) "
    f" AS"
    f" $$"
    f" BEGIN "
    f"  IF _input IS NULL THEN"
    f"      _result := ARRAY[]::UUID[];"
    f"      RETURN;"
    f"  END IF;"
    f"  _result := _input;"
    f" END;"
    f" $$ "
    f" LANGUAGE PlPgSql "
    f" ;")

base64_2_text: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.base64_2_text} (_base64_text TEXT) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT {BFn.convert_from}( {BFn.decode}(_base64_text, 'base64') , 'UTF8')"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

text_2_base64: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.text_2_base64} (_text TEXT) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT {BFn.encode}(_text::BYTEA, 'base64')"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

# @ref https://stackoverflow.com/questions/75998761/how-to-escape-a-in-a-string-before-casting-to-a-bytea
db_text_2_base64: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.db_text_2_base64} (_text TEXT) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT {BFn.translate}({BFn.encode}({BFn.replace}(_text, '\\', '\\\\')::BYTEA, 'base64'), E'\n', '')"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

db_image_2_base64: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.db_image_2_base64} (_image BYTEA) "
    f" RETURNS TEXT "
    f" AS"
    f" $$"
    f"   SELECT {BFn.translate}({BFn.encode}(_image, 'base64'), E'\n', '')"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

base64_2_db_image: Final = (
    f" CREATE OR REPLACE FUNCTION "
    f" {CFn.base64_2_db_image} (_base64_text TEXT) "
    f" RETURNS BYTEA "
    f" AS"
    f" $$"
    f"   SELECT {BFn.decode}(_base64_text, 'base64')"
    f" $$ "
    f" STRICT"
    f" LANGUAGE SQL "
    f" IMMUTABLE;")

def insert_util_fn__general(conn):
    insert_function(is_null, CFn.is_null, conn)
    insert_function(array_sort, CFn.array_sort, conn)
    insert_function(array_sort_unique, CFn.array_sort_unique, conn)
    insert_function(if_null_2_empty_bigint_array, CFn.if_null_2_empty_bigint_array, conn)
    insert_function(if_null_2_empty_uuid_array, CFn.if_null_2_empty_uuid_array, conn)
    insert_function(is_text_in_array, CFn.is_text_in_array, conn)
    insert_function(text_2_base64, CFn.text_2_base64, conn)
    insert_function(db_image_2_base64, CFn.db_image_2_base64, conn)
    insert_function(base64_2_db_image, CFn.base64_2_db_image, conn)
    insert_function(db_text_2_base64, CFn.db_text_2_base64, conn)
    insert_function(base64_2_text, CFn.base64_2_text, conn)
