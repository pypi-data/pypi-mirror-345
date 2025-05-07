import abc


class AInsertFunction(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def build_functions(self) -> list:
        raise NotImplementedError

    def build_view(self) -> list:
        return list()

    def insert_functions(self, conn, do_commit: bool = True):
        cursor = conn.cursor()
        for view in self.build_view():
            cursor.execute(view)
        for function in self.build_functions():
            cursor.execute(function)
        if do_commit:
            conn.commit()
