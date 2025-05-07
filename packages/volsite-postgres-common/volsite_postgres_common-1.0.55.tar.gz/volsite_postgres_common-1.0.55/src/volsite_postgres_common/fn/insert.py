def insert_function(fn: str, name: str, conn):
    cursor = conn.cursor()
    cursor.execute(fn)
    print(f"Inserted fn [{name}].")
