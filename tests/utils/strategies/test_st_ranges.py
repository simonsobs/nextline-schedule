from typing import Optional, TypeVar

from hypothesis import given, settings
from hypothesis import strategies as st

from nextline_schedule.utils import safe_compare, safe_max
from nextline_schedule.utils.strategies import (
    StMinMaxValuesFactory,
    st_datetimes,
    st_graphql_ints,
    st_none_or,
    st_ranges,
)

T = TypeVar('T')


def st_min_max_start(
    st_: StMinMaxValuesFactory[T],
) -> st.SearchStrategy[tuple[Optional[T], Optional[T]]]:
    def st_min() -> st.SearchStrategy[Optional[T]]:
        return st_none_or(st_())

    def st_max(min_value: Optional[T]) -> st.SearchStrategy[Optional[T]]:
        return st_none_or(st_(min_value=min_value))

    return st_min().flatmap(lambda min_: st.tuples(st.just(min_), st_max(min_)))


def st_min_max_end(
    st_: StMinMaxValuesFactory[T],
    min_start: Optional[T] = None,
) -> st.SearchStrategy[tuple[Optional[T], Optional[T]]]:
    def st_min() -> st.SearchStrategy[Optional[T]]:
        return st_none_or(st_(min_value=min_start))

    def st_max(min_value: Optional[T]) -> st.SearchStrategy[Optional[T]]:
        min_value = safe_max((min_value, min_start))
        return st_none_or(st_(min_value=min_value))

    return st_min().flatmap(lambda min_: st.tuples(st.just(min_), st_max(min_)))


@given(st.data())
@settings(max_examples=1000)
def test_st_ranges(data: st.DataObject) -> None:
    st_ = data.draw(st.sampled_from([st_graphql_ints, st_datetimes]))

    min_start, max_start = data.draw(st_min_max_start(st_=st_))  # type: ignore
    min_end, max_end = data.draw(st_min_max_end(st_=st_, min_start=min_start))  # type: ignore

    assert safe_compare(min_start) <= safe_compare(max_start)
    assert safe_compare(min_start) <= safe_compare(min_end) <= safe_compare(max_end)

    allow_start_none = data.draw(st.booleans())
    allow_end_none = data.draw(st.booleans())
    allow_equal = data.draw(st.booleans())
    let_end_none_if_start_none = data.draw(st.booleans())

    start, end = data.draw(
        st_ranges(
            st_=st_,  # type: ignore
            min_start=min_start,
            max_start=max_start,
            min_end=min_end,
            max_end=max_end,
            allow_start_none=allow_start_none,
            allow_end_none=allow_end_none,
            allow_equal=allow_equal,
            let_end_none_if_start_none=let_end_none_if_start_none,
        )
    )

    if not allow_start_none:
        assert start is not None

    if start is None and let_end_none_if_start_none:
        assert end is None
    elif not allow_end_none:
        assert end is not None

    if allow_equal:
        assert safe_compare(start) <= safe_compare(end)
    else:
        assert safe_compare(start) < safe_compare(end)

    assert safe_compare(min_start) <= safe_compare(start) <= safe_compare(max_start)
    assert safe_compare(min_end) <= safe_compare(end) <= safe_compare(max_end)
