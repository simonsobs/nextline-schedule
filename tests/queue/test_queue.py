import asyncio
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from nextline_schedule.queue import QueueEmpty, QueueItem
from nextline_schedule.queue.strategies import st_push_arg, st_queue


class StatefulTest:
    def __init__(self, data: st.DataObject) -> None:
        self._draw = data.draw
        self._queue = data.draw(st_queue())
        self._expected = list[list[QueueItem]]()

    async def _subscribe(self) -> list[list[QueueItem]]:
        return [i async for i in self._queue.subscribe()]

    def _on_expected_publish(self) -> None:
        self._expected.append(list(self._queue.items))

    async def call(self) -> None:
        empty = not self._queue
        if empty:
            with pytest.raises(QueueEmpty):
                await self._queue()
        else:
            script = await self._queue()
            assert isinstance(script, str)
            self._on_expected_publish()

    async def pop(self) -> None:
        empty = not self._queue
        if empty:
            assert await self._queue.pop() is None
        else:
            item = await self._queue.pop()
            assert item is not None
            self._on_expected_publish()

    async def push(self) -> None:
        arg = self._draw(st_push_arg())
        await self._queue.push(arg)
        self._on_expected_publish()

    async def remove(self) -> None:
        ids = [i.id for i in self._queue.items]
        ids.append(self._draw(st.integers(min_value=0)))
        id = self._draw(st.sampled_from(ids))
        success = await self._queue.remove(id)
        if success:
            self._on_expected_publish()

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


@settings(max_examples=500)
@given(data=st.data())
async def test_property(data: st.DataObject) -> None:
    test = StatefulTest(data)

    METHODS = [
        test.call,
        test.pop,
        test.push,
        test.remove,
    ]

    methods = data.draw(st.lists(st.sampled_from(METHODS)))

    async with test:
        for method in methods:
            await asyncio.sleep(0)
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
