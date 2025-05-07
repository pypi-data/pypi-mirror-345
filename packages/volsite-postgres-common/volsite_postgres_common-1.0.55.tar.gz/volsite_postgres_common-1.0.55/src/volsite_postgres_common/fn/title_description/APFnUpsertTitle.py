import abc
from abc import ABC
from typing import Final

from volsite_postgres_common.db.CC import CC
from volsite_postgres_common.db.FnT import FnT
from volsite_postgres_common.fn.function import ASqlFunction, Arg


class APFnUpsertTitle(ASqlFunction, ABC):
    _title_: Final[str] = '_title_'

    @abc.abstractmethod
    def table_title(self) -> str:  # {ScT.mentor.titles}
        raise NotImplementedError

    @abc.abstractmethod
    def col_title_id(self) -> str:  # {C.title_id}
        raise NotImplementedError

    def in_args(self) -> list:
        return [
            Arg(self._title_, FnT.TEXT)
        ]

    def return_type(self) -> FnT:
        return FnT.BIGINT

    def body(self) -> str:
        return (
            f" INSERT INTO {self.table_title()} ("
            f"     {CC.text}, {CC.length}, {CC.built_time}, {CC.last_used_time}) "
            f" VALUES (trim({self._title_}), length(trim({self._title_})), current_timestamp, current_timestamp) "
            f" ON CONFLICT({CC.text}) "
            f"     DO"
            f"         UPDATE SET "
            f"             {CC.used_count} = {self.table_title()}.{CC.used_count} + 1,  "
            f"             {CC.last_used_time} = current_timestamp"
            f" RETURNING {self.col_title_id()};"
        )
