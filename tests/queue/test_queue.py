import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline_schedule.queue import QueueEmpty, QueueItem
from nextline_schedule.queue.strategies import st_push_arg, st_queue


class StatefulTest:
    def __init__(self, data: st.DataObject) -> None:
        self._draw = data.draw
        self._queue = data.draw(st_queue())
        self._expected = list[list[QueueItem]]()

    @asynccontextmanager
    async def context(self) -> AsyncIterator[None]:
        await asyncio.sleep(0)
        self._ids = [i.id for i in self._queue.items]
        assert len(self._ids) == len(self._queue)
        yield

    async def _subscribe(self) -> list[list[QueueItem]]:
        return [i async for i in self._queue.subscribe()]

    def _on_expected_publish(self) -> None:
        self._expected.append(list(self._queue.items))

    async def call(self) -> None:
        if not self._ids:
            with pytest.raises(QueueEmpty):
                await self._queue()
            ids = [i.id for i in self._queue.items]
            assert ids == self._ids
        else:
            expected = self._queue.items[0].script
            script = await self._queue()
            assert script == expected
            ids = [i.id for i in self._queue.items]
            assert ids == self._ids[1:]
            self._on_expected_publish()

    async def pop(self) -> None:
        if not self._ids:
            assert await self._queue.pop() is None
            ids = [i.id for i in self._queue.items]
            assert ids == self._ids
        else:
            item = await self._queue.pop()
            assert item is not None
            assert item.id == self._ids[0]
            ids = [i.id for i in self._queue.items]
            assert ids == self._ids[1:]
            self._on_expected_publish()

    async def push(self) -> None:
        arg = self._draw(st_push_arg())
        item = await self._queue.push(arg)
        assert item.name == arg.name
        id = item.id
        ids = [i.id for i in self._queue.items]
        assert ids[-1] == id
        assert ids[:-1] == self._ids
        self._on_expected_publish()

    async def remove(self) -> None:
        fake_id = max(self._ids, default=0) + 1
        id = self._draw(st.sampled_from([*self._ids, fake_id]))
        success = await self._queue.remove(id)
        ids = [i.id for i in self._queue.items]
        if id in self._ids:
            assert success
            idx = self._ids.index(id)
            assert [*ids[:idx], id, *ids[idx:]] == self._ids
            self._on_expected_publish()
        else:
            assert not success
            assert ids == self._ids

    async def move_to_first(self) -> None:
        fake_id = max(self._ids, default=0) + 1
        id = self._draw(st.sampled_from([*self._ids, fake_id]))
        success = await self._queue.move_to_first(id)
        ids = [i.id for i in self._queue.items]
        if id in self._ids:
            assert success
            idx = self._ids.index(id)
            assert ids[0] == id
            assert [*ids[1 : idx + 1], ids[0], *ids[idx + 1 :]] == self._ids
            self._on_expected_publish()
        else:
            assert not success
            assert ids == self._ids

    async def move_to_last(self) -> None:
        fake_id = max(self._ids, default=0) + 1
        id = self._draw(st.sampled_from([*self._ids, fake_id]))
        success = await self._queue.move_to_last(id)
        ids = [i.id for i in self._queue.items]
        if id in self._ids:
            assert success
            idx = self._ids.index(id)
            assert ids[-1] == id
            assert [*ids[:idx], ids[-1], *ids[idx:-1]] == self._ids
            self._on_expected_publish()
        else:
            assert not success
            assert ids == self._ids

    async def move_one_forward(self) -> None:
        fake_id = max(self._ids, default=0) + 1
        id = self._draw(st.sampled_from([*self._ids, fake_id]))
        success = await self._queue.move_one_forward(id)
        ids = [i.id for i in self._queue.items]
        idx = None if id not in self._ids else self._ids.index(id)
        if idx:  # >= 1
            assert success
            assert ids[idx - 1] == id
            assert [
                *ids[: idx - 1],
                ids[idx],
                ids[idx - 1],
                *ids[idx + 1 :],
            ] == self._ids
            self._on_expected_publish()
        else:
            assert not success
            assert ids == self._ids

    async def move_one_backward(self) -> None:
        fake_id = max(self._ids, default=0) + 1
        id = self._draw(st.sampled_from([*self._ids, fake_id]))
        success = await self._queue.move_one_backward(id)
        ids = [i.id for i in self._queue.items]
        idx = None if id not in self._ids else self._ids.index(id)
        if idx is not None and idx != len(self._ids) - 1:
            assert success
            assert ids[idx + 1] == id
            assert [*ids[:idx], ids[idx + 1], ids[idx], *ids[idx + 2 :]] == self._ids
            self._on_expected_publish()
        else:
            assert not success
            assert ids == self._ids

    async def __aenter__(self) -> 'StatefulTest':
        self._task = asyncio.create_task(self._subscribe())
        await asyncio.sleep(0)
        await self._queue.__aenter__()
        self._on_expected_publish()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._queue.__aexit__(*args, **kwargs)
        await asyncio.sleep(0)
        actual = await self._task
        assert self._expected == actual


@settings(max_examples=500, phases=(Phase.generate,))
@given(data=st.data())
async def test_property(data: st.DataObject) -> None:
    test = StatefulTest(data)

    METHODS = [
        test.call,
        test.pop,
        test.push,
        test.remove,
        test.move_to_first,
        test.move_to_last,
        test.move_one_forward,
        test.move_one_backward,
    ]

    methods = data.draw(st.lists(st.sampled_from(METHODS)))

    async with test:
        for method in methods:
            async with test.context():
                await method()

    await cancel_extra_tasks()


async def cancel_extra_tasks() -> None:
    # For unknown reasons, the task created by `queue.subscribe()` in the
    # `_subscribe` method is sometimes still running.
    extra_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for t in extra_tasks:  # pragma: no cover
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
