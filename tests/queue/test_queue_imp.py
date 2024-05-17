from hypothesis import given

from nextline_schedule.queue.strategies import (
    PushArg,
    QueueImp,
    st_push_arg,
    st_queue_imp,
)


@given(queue=st_queue_imp())
def test_queue(queue: QueueImp):
    # __len__
    assert len(queue) == len(queue.items)

    # Unique ids
    assert len(set(i.id for i in queue.items)) == len(queue)


@given(queue=st_queue_imp(), push_arg=st_push_arg())
def test_push(queue: QueueImp, push_arg: PushArg):
    initial_len = len(queue)
    item = queue.push(push_arg)
    assert item.script == push_arg.script
    assert len(queue) == initial_len + 1
    assert len(set(i.id for i in queue.items)) == len(queue)


@given(queue=st_queue_imp())
def test_pop(queue: QueueImp):
    initial_len = len(queue)
    if initial_len == 0:
        assert queue.pop() is None
        return
    item = queue.pop()
    assert len(queue) == initial_len - 1
    assert item not in queue.items


@given(queue=st_queue_imp())
def test_remove(queue: QueueImp):
    initial_len = len(queue)
    if initial_len == 0:
        assert not queue.remove(0)
        return
    item = queue.items[0]
    assert queue.remove(item.id)
    assert len(queue) == initial_len - 1
    assert item not in queue.items
    assert not queue.remove(item.id)
    assert len(queue) == initial_len - 1
    assert item not in queue.items
