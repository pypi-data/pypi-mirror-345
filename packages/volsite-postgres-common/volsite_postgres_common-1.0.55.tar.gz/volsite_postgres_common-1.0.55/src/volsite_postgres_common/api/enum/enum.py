def create_enum_type(name: str, enum, conn):
    cursor = conn.cursor()
    enum_lst = list()
    for n in all_enum_values(enum):
        enum_lst.append(f"'{n}'")
    sql = f"DROP TYPE IF EXISTS {name} CASCADE; " \
          f"CREATE TYPE {name} AS ENUM ({','.join(enum_lst)});"
    # print(sql)
    cursor.execute(sql)
    # print(f"Inserted enum type [{name}].")


def all_enum_values(cls) -> list:
    role_names = [member.value for role, member in cls.__members__.items()]
    return role_names


def all_enum_names(cls) -> list:
    val_list = all_enum_values(cls)
    res = list()
    for v in val_list:
        res.append(cls(v).name)
    return res
