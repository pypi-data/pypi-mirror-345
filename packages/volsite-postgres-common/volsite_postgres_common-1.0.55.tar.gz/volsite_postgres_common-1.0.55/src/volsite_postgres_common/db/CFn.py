from typing import Final


# ====== CFn: Common Custom Function ======
class CFn:
    schema: Final[str] = 'cfn'
    array_sort: Final[str] = f'{schema}.array_sort'
    array_sort_unique: Final[str] = f'{schema}.array_sort_unique'

    bigint_2_id: Final[str] = f'{schema}.bigint_2_id'
    bigint_array_2_id_array: Final[str] = f'{schema}.bigint_array_2_id_array'

    count_jsonb_keys: Final[str] = f'{schema}.count_jsonb_keys'

    http_status_data: Final[str] = f'{schema}.http_status_data'
    http_status_error: Final[str] = f'{schema}.http_status_error'
    http_status_error_code_only: Final[str] = f'{schema}.http_status_error_code_only'

    id_2_bigint: Final[str] = f'{schema}.id_2_bigint'
    id_2_int: Final[str] = f'{schema}.id_2_int'
    if_null_2_empty_bigint_array: Final[str] = f'{schema}.if_null_2_empty_bigint_array'
    if_null_2_empty_uuid_array: Final[str] = f'{schema}.if_null_2_empty_uuid_array'
    int_2_id: Final[str] = f'{schema}.int_2_id'
    is_null: Final[str] = f'{schema}.is_null'

    jsonb_add_key_value_elements: Final[str] = f'{schema}.jsonb_add_key_value_elements'
    jsonb_array_2_bigint_array: Final[str] = f'{schema}.jsonb_array_2_bigint_array'
    jsonb_array_2_int_array: Final[str] = f'{schema}.jsonb_array_2_int_array'
    jsonb_2_jsonb_array: Final[str] = f'{schema}.jsonb_2_jsonb_array'
    jsonb_array_2_smallint_array: Final[str] = f'{schema}.jsonb_array_2_smallint_array'
    jsonb_array_2_text_array: Final[str] = f'{schema}.jsonb_array_2_text_array'
    jsonb_array_2_lower_text_array: Final[str] = f'{schema}.jsonb_array_2_lower_text_array'
    jsonb_array_2_uuid_array: Final[str] = f'{schema}.jsonb_array_2_uuid_array'
    jsonb_array_2_id_array_dict: Final[str] = f'{schema}.jsonb_array_2_id_array_dict'
    jsonb_array_2_id_object_dict: Final[str] = f'{schema}.jsonb_array_2_id_object_dict'
    jsonb_remove_key: Final[str] = f'{schema}.jsonb_remove_key'
    jsonb_append_key_int_value: Final[str] = f'{schema}.jsonb_append_key_int_value'
    jsonb_error_code_result: Final[str] = f'{schema}.jsonb_error_code_result'
    jsonb_id_array_2_bigint_array: Final[str] = f'{schema}.jsonb_id_array_2_bigint_array'
    jsonb_id_array_2_int_array: Final[str] = f'{schema}.jsonb_id_array_2_int_array'

    is_text_in_array: Final[str] = f'{schema}.is_text_in_array'

    sort_jsonb_array_multi: Final[str] = f'{schema}.sort_jsonb_array_multi'

    test_current_time: Final[str] = f'{schema}.test_current_time'

    text_2_base64: Final[str] = f'{schema}.text_2_base64'
    base64_2_text: Final[str] = f'{schema}.base64_2_text'
    db_image_2_base64: Final[str] = f'{schema}.db_image_2_base64'
    base64_2_db_image: Final[str] = f'{schema}.base64_2_db_image'
    db_text_2_base64: Final[str] = f'{schema}.db_text_2_base64'

