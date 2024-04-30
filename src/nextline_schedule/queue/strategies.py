from typing import Optional

from hypothesis import strategies as st

from nextline_schedule.utils.strategies import st_datetimes, st_python_scripts

from .queue import PushArg, Queue, QueueItem


def st_queue_item() -> st.SearchStrategy[QueueItem]:
    return st.builds(
        QueueItem,
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


def st_queue_item_list(
    min_size: int = 0, max_size: Optional[int] = None
) -> st.SearchStrategy[list[QueueItem]]:
    return st.lists(st_queue_item(), min_size=min_size, max_size=max_size)


def st_queue(
    min_items_size: int = 0, max_items_size: int = 5
) -> st.SearchStrategy[Queue]:
    return st.builds(
        Queue,
        items=st_queue_item_list(min_size=min_items_size, max_size=max_items_size),
    )
