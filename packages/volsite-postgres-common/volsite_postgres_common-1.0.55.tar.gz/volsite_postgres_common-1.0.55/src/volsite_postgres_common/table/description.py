from typing import Final

from volsite_postgres_common.db.CC import CC

NULL_DESCRIPTION_ID: Final = 1


def insert_empty_description(table, description_id, cursor):
    cursor.execute(
        f" INSERT INTO {table} "
        f" ("
        f"   {description_id}, "
        f"   {CC.formatted_description}, {CC.plain_description}, {CC.length}, "
        f"   {CC.used_count}, {CC.built_time}, {CC.last_used_time}"
        f" )"
        f" VALUES"
        f" ("
        f"   {NULL_DESCRIPTION_ID}, "
        f"   '', '', 0, "
        f"   0, current_timestamp, current_timestamp"
        f" );")
