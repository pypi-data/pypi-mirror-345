from typing import Final

# ====== BFn: Postgres Build in Functions ======


class BFn:
    array_agg: Final[str] = 'array_agg'
    array_append: Final[str] = 'array_append'
    array_cat: Final[str] = 'array_cat'
    array_length: Final[str] = 'array_length'
    array_position: Final[str] = 'array_position'
    array_to_json: Final[str] = 'array_to_json'
    array_to_string: Final[str] = 'array_to_string'

    cardinality: Final[str] = 'cardinality'
    coalesce: Final[str] = 'coalesce'
    concat: Final[str] = 'concat'
    convert_from: Final[str] = 'convert_from'
    crypt: Final[str] = 'crypt'
    clock_timestamp: Final[str] = 'clock_timestamp'
    current_timestamp: Final[str] = 'current_timestamp'

    decode: Final[str] = 'decode'
    digest: Final[str] = 'digest'

    encode: Final[str] = 'encode'
    enum_range: Final[str] = 'enum_range'

    gen_salt: Final[str] = 'gen_salt'

    icount: Final[str] = 'icount'  # number of elements in array

    jsonb_array_length: Final[str] = 'jsonb_array_length'
    jsonb_agg: Final[str] = 'jsonb_agg'
    jsonb_array_elements: Final[str] = 'jsonb_array_elements'
    jsonb_array_elements_text: Final[str] = 'jsonb_array_elements_text'
    jsonb_build_array: Final[str] = 'jsonb_build_array'
    jsonb_build_object: Final[str] = 'jsonb_build_object'
    jsonb_each: Final[str] = 'jsonb_each'
    jsonb_object_agg: Final[str] = 'jsonb_object_agg'
    jsonb_object_keys: Final[str] = 'jsonb_object_keys'
    jsonb_set: Final[str] = 'jsonb_set'
    jsonb_strip_nulls: Final[str] = 'jsonb_strip_nulls'

    length: Final[str] = 'length'
    lower: Final[str] = 'lower'

    nextval: Final[str] = 'nextval'

    percentile_cont: Final[str] = 'percentile_cont'
    pg_get_serial_sequence: Final[str] = 'pg_get_serial_sequence'

    quote_ident: Final[str] = 'quote_ident'

    regexp_matches: Final[str] = 'regexp_matches'
    replace: Final[str] = 'replace'
    row_to_json: Final[str] = 'row_to_json'

    sha256: Final[str] = 'sha256'
    similarity: Final[str] = 'similarity'
    sort: Final[str] = 'sort'
    sort_asc: Final[str] = 'sort_asc'
    sort_desc: Final[str] = 'sort_desc'
    statement_timestamp: Final[str] = 'statement_timestamp'
    split_part: Final[str] = 'split_part'
    substring: Final[str] = 'substring'
    sum: Final[str] = 'sum'

    to_jsonb: Final[str] = 'to_jsonb'
    translate: Final[str] = 'translate'
    trim: Final[str] = 'trim'

    unnest: Final[str] = 'unnest'
    uniq: Final[str] = 'uniq'
    uuid_generate_v4: Final[str] = 'uuid_generate_v4'

    word_similarity: Final[str] = 'word_similarity'
