from typing import Optional

from hypothesis import strategies as st

from nextline_schedule.utils.strategies import st_datetimes, st_python_scripts

from .item import PushArg, QueueItem
from .queue import Queue
from .queue_imp import QueueImp


def st_queue_item(id: int) -> st.SearchStrategy[QueueItem]:
    return st.builds(
        QueueItem,
        id=st.just(id),
        name=st.text(),
        created_at=st_datetimes(),
        script=st_python_scripts(),
    )


def st_push_arg() -> st.SearchStrategy[PushArg]:
    return st.builds(
        PushArg,
        name=st.text(),
        script=st_python_scripts(),
    )


@st.composite
def st_queue_item_list(
    draw: st.DrawFn, min_size: int = 0, max_size: Optional[int] = None
) -> list[QueueItem]:
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    return [draw(st_queue_item(id=i)) for i in range(size)]


def st_queue_imp(
    min_items_size: int = 0, max_items_size: int = 5
) -> st.SearchStrategy[QueueImp]:
    return st.builds(
        QueueImp,
        items=st_queue_item_list(min_size=min_items_size, max_size=max_items_size),
    )


def st_queue(
    min_items_size: int = 0, max_items_size: int = 5
) -> st.SearchStrategy[Queue]:
    return st.builds(
        Queue,
        items=st_queue_item_list(min_size=min_items_size, max_size=max_items_size),
    )
