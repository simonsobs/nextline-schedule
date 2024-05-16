import asyncio

from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.queue import QueueItem
from nextline_schedule.queue.strategies import st_pubsub_queue, st_push_arg


@given(st.data())
async def test_pubsub_queue(data: st.DataObject):
    queue = data.draw(st_pubsub_queue())

    async def subscribe() -> list[list[QueueItem]]:
        return [i async for i in queue.subscribe()]

    task = asyncio.create_task(subscribe())
    await asyncio.sleep(0)

    METHODS = ['push', 'pop', 'remove', 'break']
    methods = data.draw(st.lists(st.sampled_from(METHODS), min_size=0, max_size=10))

    async with queue:
        expected = [queue.items]
        for method in methods:
            await asyncio.sleep(0)
            match method:
                case 'push':
                    arg = data.draw(st_push_arg())
                    await queue.push(arg)
                case 'pop':
                    item = await queue.pop()
                    if item is None:
                        continue
                case 'remove':
                    ids = [i.id for i in queue.items]
                    ids.append(st.integers(min_value=0))
                    id = data.draw(st.sampled_from(ids))
                    success = await queue.remove(id)
                    if not success:
                        continue
                case 'break':
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
