import asyncio
import time
from collections.abc import Callable
from typing import NoReturn

from nextline import Nextline
from nextline_schedule.auto import AutoMode

from .funcs import pull_func_factory


class MockError(Exception):
    pass


def f() -> None:  # pragma: no cover
    time.sleep(0.001)


def g() -> NoReturn:  # pragma: no cover
    time.sleep(0.001)
    raise MockError()


async def test_on_raised_while_pulling() -> None:
    async def pull() -> NoReturn:
        raise MockError()

    nextline = Nextline(statement=f, timeout_on_exit=60)
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await auto_mode.turn_on()
            async for state in auto_mode.subscribe_state():
                if state == 'off':  # pragma: no branch
                    break

    expected = ['off', 'auto_waiting', 'auto_pulling', 'off']
    assert expected == await states


async def test_on_raised_while_running() -> None:
    async def pull() -> Callable[[], None]:
        return g

    nextline = Nextline(statement=f, timeout_on_exit=60)
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await auto_mode.turn_on()
            async for state in auto_mode.subscribe_state():
                if state == 'off':
                    break

    expected = ['off', 'auto_waiting', 'auto_pulling', 'auto_running', 'off']
    assert expected == await states


async def subscribe_state(auto_mode: AutoMode) -> list[str]:
    return [state async for state in auto_mode.subscribe_state()]
