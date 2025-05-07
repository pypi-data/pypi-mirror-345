from volworld_common.api.CA import CA
from volworld_common.util.Base64Utf8 import Base64Utf8
from datetime import datetime
from aenum import IntEnum

def assert_sorted_books_by_title(books, title_map, direction: str, compared_end: int):
    # books = resp[CA.Data][CA.Book]
    title_ids = list()
    for b in books:
        title_ids.append(b[CA.TitleIid])
    # title_map = resp[CA.Data][CA.Title]

    title_str = list()
    title_str_sorted = list()
    for t_id in title_ids:
        title_text = Base64Utf8.decode(title_map[t_id])
        print(f"title_text = [{title_text}] --> {title_text[0:compared_end]}")
        title_str.append(title_text)
        title_str_sorted.append(title_text)
    title_str_sorted.sort()
    if direction != CA.Ascending:
        title_str_sorted.reverse()
    for t_ind in range(len(title_str)):
        assert title_str[t_ind][0:compared_end] == \
               title_str_sorted[t_ind][0:compared_end], title_str_sorted[t_ind][0:compared_end]

class SortType(IntEnum):
    String = 0
    Int = 1
    DateTime = 50

def assert_sorted_books(books, val_name: str, read_fn, direction=CA.Ascending, sort_type: SortType=SortType.String):  # , ext_total_count=16):
    asc = False
    if direction == CA.Ascending:
        asc = True
    # books = resp[CA.Data][CA.Book]

    count_results = list()
    count_sorted = list()
    # total_count = 0
    for b in books:
        value = read_fn(b)  # b[CA.Info][CA.Time][CA.Update]
        # total_count = b[CA.TotalCount]
        print(f"{val_name} = [{value}]")
        if sort_type == SortType.DateTime:
            date_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
            value = date_value
        count_results.append(value)
        count_sorted.append(value)
    # assert total_count == ext_total_count
    count_sorted.sort()
    if not asc:
        count_sorted.reverse()
    for t_ind in range(len(count_results)):
        print(f"Verify Sorted {count_results[t_ind]} == {count_sorted[t_ind]} = Python Sorted")
        assert count_results[t_ind] == count_sorted[t_ind],\
            f"{count_results[t_ind]} != {count_sorted[t_ind]} = Python Sorted"
