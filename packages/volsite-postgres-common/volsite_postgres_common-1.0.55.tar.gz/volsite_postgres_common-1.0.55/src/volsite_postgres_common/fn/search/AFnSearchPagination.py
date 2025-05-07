import abc
from volworld_common.api.CA import CA

from typing import Final
from volsite_postgres_common.db.BFn import BFn
from volsite_postgres_common.db.CFn import CFn
from volsite_postgres_common.db.FnT import FnT
from volsite_postgres_common.fn.function import AJsonPlPgSqlFunction, Arg


class AFnSearchPagination(AJsonPlPgSqlFunction, metaclass=abc.ABCMeta):
    # ====== <Search>
    _search: Final[str] = "_search"
    _permission: Final[str] = "_permission"

    _sort_by: Final[str] = "_sort_by"

    _page: Final[str] = "_page"
    _item_per_page: Final[str] = "_item_per_page"
    _page_info: Final[str] = "_page_info"

    _total_count_without_filter: Final[str] = "_total_count_without_filter"

    _tmp_results: Final[str] = "_tmp_results"
    _tmp_total_count: Final[str] = "_tmp_total_count"

    def declare(self) -> list:
        return [
            Arg(self._search, FnT.TEXT_ARRAY),
            Arg(self._permission, FnT.TEXT),

            Arg(self._sort_by, FnT.TEXT),

            Arg(self._page, FnT.INT),
            Arg(self._item_per_page, FnT.INT),
            Arg(self._page_info, FnT.JSONB),

            Arg(self._total_count_without_filter, FnT.INT),

            Arg(self._tmp_results, FnT.JSONB),
            Arg(self._tmp_total_count, FnT.INT),
        ]

    def __init__(self):
        self.defaults = {
            CA.Privilege: CA.All,
            CA.SortBy: CA.TitleIid,
            CA.Page: 1,
            CA.ItemPerPage: 10
        }
        self.min_values = {
            CA.ItemPerPage: 3
        }
        self.sort_by_values = []

    def sql__assign_privilege(self) -> str:
        return (
            f" {self._permission} := {BFn.coalesce}( "
            f"                      ({Arg.input}->>'{CA.Privilege}')::TEXT, '{self.defaults[CA.Privilege]}'"
            f"                      );"
        )

    def sql__assign_search(self) -> str:
        if not self.support_search():
            return ''

        return (
            f" {self._search} := {CFn.jsonb_array_2_text_array}(({Arg.input}->>'{CA.Search}')::JSONB);"
        )

    def sql__assign_sort_by(self) -> str:
        sort_by_list = "','".join(self.sort_by_values)
        sort_by_list = "'" + sort_by_list + "'"
        return (
            f" {self._sort_by} := {BFn.coalesce}( "
            f"                      ({Arg.input}->>'{CA.SortBy}')::TEXT, '{self.defaults[CA.SortBy]}'"
            f"                      );"
            f" IF NOT {CFn.is_text_in_array}({self._sort_by}, ARRAY[{sort_by_list}]) THEN"
            f"   {self._sort_by} :=  '{self.defaults[CA.SortBy]}';"
            f" END IF;"
        )

    def sql__assign_page(self) -> str:
        return (
            f" {self._page} := {BFn.coalesce}( ({Arg.input}->>'{CA.Page}')::INT, {self.defaults[CA.Page]});"
            f" IF {self._page} < 1 THEN {self._page} = 1; END IF;"
            f" {self._page} := {self._page} - 1;"
            f" IF {self._page} < 0 THEN {self._page} := 0;  END IF;"
        )

    def sql__assign_item_per_page(self) -> str:
        min_item_per_page = self.min_values[CA.ItemPerPage]
        return (
            f" {self._item_per_page} :=  {BFn.coalesce}( "
            f"                              ({Arg.input}->>'{CA.ItemPerPage}')::INT, {self.defaults[CA.ItemPerPage]}"
            f"                           );"
            f" IF {self._item_per_page} < {min_item_per_page} "
            f" THEN {self._item_per_page} := {min_item_per_page};  "
            f" END IF;"
        )

    def sort_direction_att(self) -> str:
        pass

    def support_search(self) -> bool:
        return True

    def sql__common_page_info(self) -> str:
        sql = (

            f"                          '{CA.ItemPerPage}', {self._item_per_page},"
            f"                          '{CA.Page}', {self._page} + 1,"
            f"                          '{CA.SortBy}', {self._sort_by},"
            f"                          '{CA.SortDirection}', '{self.sort_direction_att()}'"
        )
        if self.support_search():
            sql = f"                          '{CA.Search}', {self._search}, {sql}"
        return sql

    def sql__result_page_info(self, total_count_sql: str) -> str:
        return (
            f"                      {BFn.jsonb_build_object}("
            f"                          '{CA.TotalCount}', {total_count_sql},"
            f"                          '{CA.TotalCountWithoutFilter}', -1,"
            f"                          {self.sql__common_page_info()}"
            f"                      )"
        )


    '''
    @note SHOULD set self._tmp_total_count and self._total_count_without_filter before calling this method
    '''
    def sql__default_page_info(self) -> str:
        return (
            f"                      {BFn.jsonb_build_object}("
            f"                          '{CA.TotalCount}', {self._tmp_total_count},"
            f"                          '{CA.TotalCountWithoutFilter}', {self._total_count_without_filter},"
            f"                          {self.sql__common_page_info()}"
            f"                      )"
        )