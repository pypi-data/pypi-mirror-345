from volsite_postgres_common.db.CC import CC
from volsite_postgres_common.table.description import insert_empty_description
from volsite_postgres_common.table.series import set_max_id_for_serial_column


# @note PostgreSQL treats NULL as distinct value
def create_table_descriptions(conn, sc: str, table: str):
    sc_table = f'"{sc}"."{table}"'
    cursor = conn.cursor()
    cursor.execute(
        f" CREATE TABLE IF NOT EXISTS "
        f" {sc_table} "
        f"({CC.description_id}        BIGSERIAL PRIMARY KEY, "
        f" {CC.formatted_description} TEXT NOT NULL, "
        f" {CC.plain_description}     TEXT NOT NULL, "
        f" {CC.length}                INTEGER NOT NULL, "

        f" {CC.used_count}     INTEGER   NOT NULL DEFAULT 1, "
        f" {CC.built_time}     TIMESTAMP NOT NULL, "
        f" {CC.last_used_time} TIMESTAMP NOT NULL "
        f" );")

    cursor.execute(
        f" CREATE UNIQUE INDEX {sc}_{table}_{CC.formatted_description} "
        f" ON {sc_table}({CC.formatted_description}, {CC.plain_description});")

    insert_empty_description(sc_table, CC.description_id, cursor)
    set_max_id_for_serial_column(sc, table, CC.description_id, cursor)
    conn.commit()
