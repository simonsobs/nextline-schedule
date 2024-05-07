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

    methods = ['push', 'pop', 'remove', 'break']
    cmds = data.draw(st.lists(st.sampled_from(methods), min_size=0, max_size=10))

    async with queue:
        expected = [list(queue.items)]
        for cmd in cmds:
            await asyncio.sleep(0)
            match cmd:
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
            expected.append(list(queue.items))

    await asyncio.sleep(0)

    actual = await task
    assert actual == expected
