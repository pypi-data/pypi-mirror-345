import abc

from typing import Final

from volsite_postgres_common.db.CC import CC
from volworld_common.api.CA import CA

from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.FnT import FnT
from volsite_postgres_common.fn.function import Arg
from volworld_common.api.enum.HttpStatus import HttpStatus

from volsite_postgres_common.fn.search.AFnSearchPagination import AFnSearchPagination


class AFnSearchBookList(AFnSearchPagination, metaclass=abc.ABCMeta):

    _books: Final[str] = "_books"
    _book: Final[str] = "_book"
    _title_iid_array: Final[str] = "_title_iid_array"
    _mentor_id_array: Final[str] = "_mentor_id_array"
    _titles:  Final[str] = "_titles"
    _mentors:  Final[str] = "_mentors"

    def declare(self) -> list:
        return super().declare() + [
            Arg(self._books, FnT.JSONB),
            Arg(self._book, FnT.JSONB),
            Arg(self._title_iid_array, FnT.TEXT_ARRAY),
            Arg(self._mentor_id_array, FnT.BIGINT_ARRAY),

            Arg(self._titles, FnT.JSONB),
            Arg(self._mentors, FnT.JSONB),
        ]

    @abc.abstractmethod
    def read_books(self) -> str:
        pass

    def assign_variables(self) -> str:
        return ''

    @abc.abstractmethod
    def fn_read_titles_by_ids(self) -> str:
        pass

    @abc.abstractmethod
    def fn_read_users_by_ids(self) -> str:
        pass

    # TODO Pagination
    '''
    CA.MentorId
    '''
    def body(self) -> str:
        return (
            f""  # ====== Read Books ======
            f"{self.assign_variables()}"
            f""
            f"{self.read_books()}"
            f""
            f""  # ====== Read Title and Description Text ======
            f""
            f" {self._title_iid_array} := array[]::TEXT[];"
            f" {self._mentor_id_array} := array[]::BIGINT[];"
            f""
            f" FOR {self._book} in (SELECT {BFn.jsonb_array_elements}({self._books}) elm )"
            f" LOOP "
            # f"   RAISE NOTICE ' _book = %', {self._book}; "
            f" {self._title_iid_array} := {self._title_iid_array} "
            f"          || (({self._book}->>'{CA.TitleIid}')::TEXT);"
            f" {self._mentor_id_array} := {self._mentor_id_array} "
            f"          || (({self._book}->>'{CC.mentor_id}')::BIGINT);"
            f" END LOOP;"
            f""
            f" {self._titles} := {self.fn_read_titles_by_ids()}( {BFn.jsonb_build_object}("
            f"              '{CA.TitleIid}', {BFn.array_to_json}({self._title_iid_array})"
            f"          ) "
            f"   );"
            f""
            f""

            # f"   RAISE NOTICE ' _mentor_id_array = %', {self._mentor_id_array}; "
            # f"   RAISE NOTICE ' _mentor_id_array JSON = %', {BFn.array_to_json}({self._mentor_id_array}); "
            f" {self._mentors} := {self.fn_read_users_by_ids()}( {BFn.jsonb_build_object}("
            f"              '{CC.user_id}', {BFn.array_to_json}({self._mentor_id_array})"
            f"          ) "
            f"   );"
            f""
            f""  # ====== Results ======
            f""
            f" {self.sql_set_result()}"
        )

    def sql_set_result(self) -> str:
        return (
            f" {Arg.result} := {BFn.jsonb_build_object}("
            f"    '{CA.HttpStatus}', {HttpStatus.Ok_200.value}, "
            f"          '{CA.Data}', {BFn.jsonb_build_object}("
            f"                   '{CA.TimeNow}', {BFn.current_timestamp},"
            f"                      '{CA.Page}', {self._page_info},"
            f"                     '{CA.Title}', {self._titles},"
            f"                    '{CA.Mentor}', {self._mentors},"
            f"                      '{CA.Book}', {self._books}"
            f"                      )"
            f"                 );"
        )
