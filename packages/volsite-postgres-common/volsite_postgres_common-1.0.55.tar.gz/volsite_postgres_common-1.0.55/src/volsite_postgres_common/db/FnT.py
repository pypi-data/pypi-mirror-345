from typing import Final


class FnT:  # Function Arg Types
    BIGINT: Final[str] = 'BIGINT'
    BIGINT_ARRAY : Final[str]= 'BIGINT[]'
    BOOLEAN: Final[str] = 'BOOLEAN'
    BYTEA: Final[str] = 'BYTEA'
    
    FLOAT: Final[str] = 'FLOAT'

    INT: Final[str] = 'INT'
    INT_ARRAY: Final[str] = 'INT[]'

    JSONB: Final[str] = 'JSONB'
    JSONB_ARRAY: Final[str] = 'JSONB[]'

    RECORD: Final[str] = 'RECORD'

    SMALLINT: Final[str] = 'SMALLINT'
    SMALLINT_ARRAY: Final[str] = 'SMALLINT[]'

    TEXT: Final[str] = 'TEXT'
    TEXT_ARRAY: Final[str] = 'TEXT[]'

    TIMESTAMP: Final[str] = 'TIMESTAMP'

    UUID: Final[str] = 'UUID'
    UUID_ARRAY: Final[str] = 'UUID[]'

    VOID: Final[str] = 'VOID'
