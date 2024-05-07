from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.utils import safe_compare
from nextline_schedule.utils.strategies import st_datetimes, st_ranges


@given(st.data())
def test_st_datetimes(data: st.DataObject) -> None:
    min_, max_ = data.draw(st_ranges(st_=st_datetimes))
    dt_ = data.draw(st_datetimes(min_value=min_, max_value=max_))
    assert dt_.tzinfo is None
    assert dt_.fold == 0
    assert safe_compare(min_) <= dt_ <= safe_compare(max_)
