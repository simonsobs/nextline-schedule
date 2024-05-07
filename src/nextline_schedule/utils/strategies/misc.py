from typing import Optional, Protocol, TypeVar

from graphql import GRAPHQL_MAX_INT, GRAPHQL_MIN_INT
from hypothesis import strategies as st

from nextline_schedule.utils import safe_max, safe_min

T = TypeVar('T')


class StMinMaxValuesFactory(Protocol[T]):
    def __call__(
        self, *, min_value: Optional[T] = None, max_value: Optional[T] = None
    ) -> st.SearchStrategy[T]:
        ...


def st_none_or(st_: st.SearchStrategy[T]) -> st.SearchStrategy[Optional[T]]:
    '''A strategy for `None` or values from another strategy.

    >>> v = st_none_or(st.integers()).example()
    >>> v is None or isinstance(v, int)
    True
    '''
    return st.one_of(st.none(), st_)


def st_graphql_ints(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> st.SearchStrategy[int]:
    '''A strategy for integers within the range of GraphQL's `Int` type.

    Note: GraphQL's `Int` type is a 32-bit signed integer, i.e., -2,147,483,648
    to 2,147,483,647, while SQLite's `INTEGER` type is a 64-bit signed integer.
    The range of GraphQL's `Int` type is a subset of SQLite's `INTEGER` type.

    >>> int_ = st_graphql_ints().example()
    >>> int_ >= GRAPHQL_MIN_INT
    True

    >>> int_ <= GRAPHQL_MAX_INT
    True
    '''
    min_value = safe_max((min_value, GRAPHQL_MIN_INT))
    max_value = safe_min((max_value, GRAPHQL_MAX_INT))
    return st.integers(min_value=min_value, max_value=max_value)


def st_ranges(
    st_: StMinMaxValuesFactory[T],
    min_start: Optional[T] = None,
    max_start: Optional[T] = None,
    min_end: Optional[T] = None,
    max_end: Optional[T] = None,
    allow_start_none: bool = True,
    allow_end_none: bool = True,
    let_end_none_if_start_none: bool = False,
    allow_equal: bool = True,
) -> st.SearchStrategy[tuple[Optional[T], Optional[T]]]:
    '''Generate two values (start, end) from a strategy, where start <= end.

    The minimum and maximum values can be specified by `min_start`,
    `max_start`, `min_end`, `max_end`.

    `start` (`end`) can be `None` if `allow_start_none` (`allow_end_none`) is `True`.

    If `let_end_none_if_start_none` is `True`, `end` will be always `None` when
    `start` is `None` regardless of `allow_end_none`.

    If `allow_equal` is `False`, `start` and `end` cannot be equal, i.e., `start < end`.

    >>> start, end = st_ranges(
    ...     st.integers,
    ...     min_start=0,
    ...     max_end=10,
    ...     allow_start_none=False,
    ...     allow_end_none=False,
    ... ).example()

    The results can be, for example, used as min_value and max_value of st.integers().

    >>> i = st.integers(min_value=start, max_value=end).example()
    >>> start <= i <= end
    True

    The results can also be used as min_size and max_size of st.lists().

    >>> l = st.lists(st.integers(), min_size=start, max_size=end).example()
    >>> start <= len(l) <= end
    True

    '''

    def st_start() -> st.SearchStrategy[Optional[T]]:
        _max_start = safe_min((max_start, max_end))
        _st = st_(min_value=min_start, max_value=_max_start)
        return st_none_or(_st) if allow_start_none else _st

    def st_end(start: T | None) -> st.SearchStrategy[Optional[T]]:
        _min_end = safe_max((min_start, start, min_end))
        if min_end is not None and max_end is not None:
            assert min_end <= max_end  # type: ignore
        if start is None and let_end_none_if_start_none:
            return st.none()
        _st = st_(min_value=_min_end, max_value=max_end)
        if start is not None and not allow_equal:
            _st = _st.filter(lambda x: x > start)  # type: ignore
        return st_none_or(_st) if allow_end_none else _st

    return st_start().flatmap(
        lambda start: st.tuples(st.just(start), st_end(start=start))
    )
