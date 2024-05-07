import datetime as dt
from typing import Optional

from hypothesis import strategies as st


def st_datetimes(
    min_value: Optional[dt.datetime] = None,
    max_value: Optional[dt.datetime] = None,
) -> st.SearchStrategy[dt.datetime]:
    '''A strategy for naive `datetime` objects without imaginary datetimes or folds.

    Note: timezones and folds are not supported by SQLite.

    >>> dt_ = st_datetimes().example()
    >>> dt_.tzinfo is None
    True

    >>> dt_.fold
    0
    '''
    if min_value is None:
        min_value = dt.datetime.min

    if max_value is None:
        max_value = dt.datetime.max

    return st.datetimes(
        min_value=min_value,
        max_value=max_value,
        allow_imaginary=False,
    ).map(lambda dt_: dt_.replace(fold=0))
