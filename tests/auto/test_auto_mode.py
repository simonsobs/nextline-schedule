import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

from nextline import Nextline
from nextline.utils import until_true
from nextline_schedule.auto import AutoMode, ModeName

from .funcs import STATEMENT_TEMPLATE, pull_func_factory, until_state


class StatefulTest:
    def __init__(self, data: st.DataObject) -> None:
        self._draw = data.draw
        statement = STATEMENT_TEMPLATE.format(name='init', count=1)
        self._nextline = Nextline(statement=statement)
        self._scheduler = pull_func_factory('schedule')
        self._queue = pull_func_factory('queue')
        self._auto_mode = AutoMode(
            nextline=self._nextline, scheduler=self._scheduler, queue=self._queue
        )

        assert self._auto_mode.mode == 'off'
        assert self._auto_mode.state == 'created'

    @asynccontextmanager
    async def context(self) -> AsyncIterator[None]:
        await asyncio.sleep(0)
        yield

    async def _subscribe_mode(self) -> list[str]:
        return [i async for i in self._auto_mode.subscribe_mode()]

    async def _subscribe_state(self) -> list[str]:
        return [i async for i in self._auto_mode.subscribe_state()]

    async def change_mode(self) -> None:
        MODE_NAMES: list[ModeName] = ['off', 'scheduler', 'queue']
        mode = self._draw(st.sampled_from(MODE_NAMES))
        await self._auto_mode.change_mode(mode)
        if mode == 'off':
            await until_true(lambda: self._auto_mode.mode == 'off')
            await until_true(lambda: self._auto_mode.state == 'off')
        elif mode == 'scheduler':
            await until_true(lambda: self._auto_mode.mode == 'scheduler')
            await until_true(lambda: self._auto_mode.state.startswith('auto_'))
        elif mode == 'queue':  # pragma: no branch
            await until_true(lambda: self._auto_mode.mode == 'queue')
            await until_true(lambda: self._auto_mode.state.startswith('auto_'))

    async def turn_on(self) -> None:
        await self._auto_mode.turn_on()
        await until_true(lambda: self._auto_mode.mode in ('scheduler', 'queue'))
        await until_true(lambda: self._auto_mode.state.startswith('auto_'))

    async def turn_off(self) -> None:
        await self._auto_mode.turn_off()
        await until_true(lambda: self._auto_mode.mode == 'off')
        await until_true(lambda: self._auto_mode.state == 'off')

    async def wait(self) -> None:
        if not self._auto_mode.state.startswith('auto_'):
            return
        state = self._draw(st.sampled_from(['finished', 'running']))
        count = self._draw(st.integers(min_value=1, max_value=3))

        await until_state(self._nextline, state=state, count=count)

    async def __aenter__(self) -> 'StatefulTest':
        self._mode_sub = asyncio.create_task(self._subscribe_mode())
        self._state_sub = asyncio.create_task(self._subscribe_state())

        await asyncio.sleep(0)

        await self._auto_mode.__aenter__()
        await self._nextline.__aenter__()

        assert self._auto_mode.mode == 'off'
        assert self._auto_mode.state == 'off'

        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self._nextline.__aexit__(*args, **kwargs)
        await self._auto_mode.__aexit__(*args, **kwargs)

        modes = await self._mode_sub
        states = await self._state_sub

        # assert modes == ['off']
        # assert states == ['off']


# @settings(max_examples=500, phases=(Phase.generate,))
@settings(deadline=None, phases=(Phase.generate,))
@given(data=st.data())
async def test_property(data: st.DataObject) -> None:
    test = StatefulTest(data)

    METHODS = [
        test.change_mode,
        test.turn_on,
        test.turn_off,
        test.wait,
    ]

    methods = data.draw(st.lists(st.sampled_from(METHODS), max_size=4))

    async with test:
        for method in methods:
            async with test.context():
                await method()
