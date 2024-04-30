from hypothesis import given

from nextline_schedule.queue import Queue
from nextline_schedule.queue.strategies import st_queue


@given(queue=st_queue())
def test_queue(queue: Queue):
    len(queue.items)
