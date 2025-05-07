import abc
from abc import ABC
from typing import Final

from volsite_postgres_common.db.CC import CC
from volsite_postgres_common.db.FnT import FnT
from volsite_postgres_common.fn.function import Arg, ASqlFunction


class APFnUpsertDescription(ASqlFunction, ABC):
    _formatted_: Final[str] = '_formatted_'
    _plain_: Final[str] = '_plain_'

    @abc.abstractmethod
    def table_description(self) -> str:  # {ScT.mentor__descriptions}
        raise NotImplementedError

    def in_args(self) -> list:
        return [
            Arg(self._formatted_, FnT.TEXT),
            Arg(self._plain_, FnT.TEXT)
        ]

    def return_type(self) -> FnT:
        return FnT.BIGINT

    def body(self) -> str:
        return (
            f" INSERT INTO "
            f" {self.table_description()} "
            f" ({CC.formatted_description}, "
            f"  {CC.plain_description}, "
            f"  {CC.length}, "
            f"  {CC.built_time}, {CC.last_used_time}) "
            f" VALUES (trim({self._formatted_}), "
            f"         trim({self._plain_}), "
            f"         length(trim({self._plain_})), "
            f" current_timestamp, current_timestamp) "
            f" ON CONFLICT({CC.formatted_description}, {CC.plain_description}) "
            f"   DO"
            f"     UPDATE SET "
            f"       {CC.used_count} = {self.table_description()}.{CC.used_count} + 1,  "
            f"       {CC.last_used_time} = current_timestamp"
            f" RETURNING {CC.description_id};"
            )
