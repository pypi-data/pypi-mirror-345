from volsite_postgres_common.db.CC import CC
from volsite_postgres_common.table.series import set_max_id_for_serial_column
from volsite_postgres_common.table.text import insert_empty_text


# @note PostgreSQL treats NULL as distinct value
def create_table_titles(conn, sc: str, table: str, title_id: str, add_trgm_index: bool = True):
    sc_table = f'"{sc}"."{table}"'
    cursor = conn.cursor()
    cursor.execute(
        f" CREATE TABLE IF NOT EXISTS "
        f" {sc_table} ("
        f"     {title_id}            BIGSERIAL      PRIMARY KEY, "  # 8bytes 
        f"     {CC.text}              TEXT           NOT NULL, "
        f"     {CC.length}            SMALLINT       NOT NULL, "
        f"     {CC.used_count}        INTEGER        NOT NULL DEFAULT 1, "
        f"     {CC.built_time}        TIMESTAMP      NOT NULL, "
        f"     {CC.last_used_time}    TIMESTAMP      NOT NULL );")

    if add_trgm_index:
        cursor.execute(f"CREATE INDEX trgm_idx ON {sc_table} USING GIN ({CC.text} gin_trgm_ops);")

    cursor.execute(
        f" CREATE UNIQUE INDEX {sc}_{table}_{CC.text} ON "
        f"     {sc_table}("
        f"         {CC.text});")

    insert_empty_text(sc_table, title_id, cursor)

    set_max_id_for_serial_column(sc, table, title_id, cursor)
    conn.commit()
