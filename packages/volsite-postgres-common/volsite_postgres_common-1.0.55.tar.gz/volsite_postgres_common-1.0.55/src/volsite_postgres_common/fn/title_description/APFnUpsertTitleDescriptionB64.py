import abc
from abc import ABC
from typing import Final

from volsite_postgres_common.db.FnT import FnT
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.fn.function import AJsonPlPgSqlFunction, Arg

from volworld_common.api.CA import CA


class APFnUpsertTitleDescriptionB64(AJsonPlPgSqlFunction, ABC):

    _title_id: Final[str] = '_title_id'
    _description_id: Final[str] = '_description_id'

    _title: Final[str] = '_title'
    _des_plain: Final[str] = '_des_plain'
    _des_format: Final[str] = '_des_format'

    @abc.abstractmethod
    def input_a_title(self) -> str:  # {A.Title}
        raise NotImplementedError

    @abc.abstractmethod
    def output_a_title_id(self) -> str:  # {A.TitleId}
        raise NotImplementedError

    @abc.abstractmethod
    def pfn_title___upsert(self) -> str:  # {PFn_title___upsert}
        raise NotImplementedError

    @abc.abstractmethod
    def pfn_description___upsert(self) -> str:  # {PFn_description___upsert}
        raise NotImplementedError

    def declare(self) -> list:
        return [
            Arg(self._title_id, FnT.BIGINT),
            Arg(self._description_id, FnT.BIGINT),

            Arg(self._title, FnT.TEXT),
            Arg(self._des_plain, FnT.TEXT),
            Arg(self._des_format, FnT.TEXT)
        ]

    def body(self) -> str:
        return (
            f" {self._title} := {BFn.convert_from}( "
            f"      {BFn.decode}( ({Arg.input}->>'{self.input_a_title()}')::{FnT.TEXT}, 'base64'), 'UTF-8');"
            f" {self._des_plain} := {BFn.convert_from}( "
            f"      {BFn.decode}( ({Arg.input}->>'{CA.DescriptionPlain}')::{FnT.TEXT}, 'base64'), 'UTF-8');"
            f" {self._des_format} := {BFn.convert_from}( "
            f"      {BFn.decode}( ({Arg.input}->>'{CA.DescriptionFormatted}')::{FnT.TEXT}, 'base64'), 'UTF-8');"
            f""
            f" {self._title_id} := {self.pfn_title___upsert()}({self._title}); "
            f" {self._description_id} := {self.pfn_description___upsert()}({self._des_format}, {self._des_plain}); "
            f" {Arg.result} := {BFn.jsonb_build_object}("
            f"       '{self.output_a_title_id()}', {CFn.bigint_2_id}({self._title_id}),"
            f"       '{CA.DescriptionIid}', {CFn.bigint_2_id}({self._description_id}) "
            f"   );"
        )
