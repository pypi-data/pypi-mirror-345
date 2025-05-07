def drop_all_schema_data_and_insert_schema(sc: str, conn):
    cursor = conn.cursor()
    cursor.execute(f'DROP SCHEMA IF EXISTS {sc} CASCADE;')
    cursor.execute(f'CREATE SCHEMA {sc};')
