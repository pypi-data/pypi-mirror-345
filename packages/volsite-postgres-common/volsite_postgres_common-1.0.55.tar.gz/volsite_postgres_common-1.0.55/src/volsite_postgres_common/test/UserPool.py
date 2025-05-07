from volworld_common.util.id_util import new_rand_test_user_name, rand_uuid
from volworld_common.test.behave.BehaveUtil import BehaveUtil

class UserInfo:
    def __init__(self, name: str, password: str = None):
        name = BehaveUtil.clear_string(name)
        self.name: str = name
        # for testing wrong formatted username, put the name before generated id
        self.used_name: str = f"{self.name}xxxxxx{new_rand_test_user_name()}"
        self.password: str = password
        self.user_uuid: str = rand_uuid()
        self.user_id: int | None = None


class UserPool:
    def __init__(self):
        self.users = dict()

    def add_user(self, name: str, password: str = None) -> UserInfo:
        name = BehaveUtil.clear_string(name)
        assert name not in self.users
        self.users[name] = UserInfo(name, password)
        return self.users[name]

    def get_user(self, name: str) -> UserInfo:
        name = BehaveUtil.clear_string(name)
        if name not in self.users:
            return None

        return self.users[name]
