import asyncio

from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.queue import QueueEmpty, QueueItem
from nextline_schedule.queue.strategies import st_push_arg, st_queue


@given(st.data())
async def test_queue(data: st.DataObject):
    queue = data.draw(st_queue())

    async def subscribe() -> list[list[QueueItem]]:
        return [i async for i in queue.subscribe()]

    task = asyncio.create_task(subscribe())
    await asyncio.sleep(0)

    METHODS = ['call', 'pop', 'push', 'remove', 'break']
    methods = data.draw(st.lists(st.sampled_from(METHODS), min_size=0, max_size=10))

    async with queue:
        expected = [queue.items]
        for method in methods:
            await asyncio.sleep(0)
            empty = not queue
            match method, empty:
                case 'call', True:
                    try:
                        await queue()
                    except QueueEmpty:
                        continue
                case 'call', False:
                    script = await queue()
                    assert isinstance(script, str)
                case 'pop', True:
                    assert await queue.pop() is None
                    continue
                case 'pop', False:
                    item = await queue.pop()
                    assert item is not None
                case 'push', _:
                    arg = data.draw(st_push_arg())
                    await queue.push(arg)
                case 'remove', _:
                    ids = [i.id for i in queue.items]
                    ids.append(st.integers(min_value=0))
                    id = data.draw(st.sampled_from(ids))
                    success = await queue.remove(id)
                    if not success:
                        continue
                case 'break', _:
                    break
                case _:  # pragma: no cover
                    raise ValueError(f'Invalid method: {method!r}')
            expected.append(list(queue.items))

    await asyncio.sleep(0)

    actual = await task
    assert actual == expected

    # Cancel extra tasks. For unknown reasons, the task created by
    # `queue.subscribe()` in the `subscribe` function is sometimes still running.
    extra_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for t in extra_tasks:  # pragma: no cover
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
