from typing import Final

from volsite_postgres_common.db.CC import CC

NULL_TEXT_ID: Final = 1
DEFAULT_NOTE_TYPE_NAME_ID: Final = 10


def insert_empty_text(table, text_id, cursor):
    cursor.execute(
        f" INSERT INTO {table} ("
        f"     {text_id}, "
        f"     {CC.text}, {CC.length}, "
        f"     {CC.used_count}, {CC.built_time}, {CC.last_used_time} )"
        f" VALUES ("
        f"     {NULL_TEXT_ID}, "
        f"     '', 0,"
        # f"     '$$$sys_null$$$', 0,"
        f"     0, current_timestamp, current_timestamp);")

    cursor.execute(
        f" INSERT INTO {table} ("
        f"     {text_id}, "
        f"     {CC.text}, {CC.length}, "
        f"     {CC.used_count}, {CC.built_time}, {CC.last_used_time} )"
        f" VALUES ("
        f"     {DEFAULT_NOTE_TYPE_NAME_ID}, "
        f"     '$$@$$_NoteType', 0,"
        # f"     '$$$sys_null$$$', 0,"
        f"     0, current_timestamp, current_timestamp);")
