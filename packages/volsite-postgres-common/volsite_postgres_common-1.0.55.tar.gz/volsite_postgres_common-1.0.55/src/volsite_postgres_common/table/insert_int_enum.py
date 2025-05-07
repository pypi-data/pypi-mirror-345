from enum import IntEnum

from volsite_postgres_common.db.CC import CC
from volsite_postgres_common.db.FnT import FnT


def create_table___enum_table(schema, table, type_key: str, conn):
    schema_table = f'{schema}.{table}'
    print(f"create_table___enum_int__{schema_table}...")
    cursor = conn.cursor()
    cursor.execute(
        f'CREATE TABLE IF NOT EXISTS {schema_table} '
        f'('
        f' {type_key}     {FnT.SMALLINT}  PRIMARY KEY NOT NULL ,'
        f' {CC.name}       {FnT.TEXT}  NOT NULL'
        f');')

    cursor.execute(
        f'CREATE UNIQUE INDEX {schema}_{table}_name'
        f' ON {schema_table}({CC.name});')

def insert_int_enum(schema: str, table: str, type_name: str, enum_class) -> str:
    schema_table = f'{schema}.{table}'
    insert = f"INSERT INTO {schema_table} ( {CC.name}, {type_name} ) VALUES "
    values = ""
    init = True
    for e in enum_class:
        if not init:
            values += ","
        values += f"('{e.name}', {e.value})"
        init = False
    values += ";"
    return insert + values



def create_and_insert_int_enum_table(schema: str, table: str, type_name: str, enum_class, conn):
    create_table___enum_table(schema, table, type_name, conn)

    conn.cursor().execute(
        insert_int_enum(schema, table, type_name, enum_class)
    )