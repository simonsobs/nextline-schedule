import asyncio
import time

from nextline import Nextline

from nextline_schedule.auto import AutoMode, AutoModeStateMachine

STATEMENT_QUEUE = '''
"""queue"""
import time
time.sleep(0.01)
'''


async def mock_queue() -> str:
    return STATEMENT_QUEUE


class MockError(Exception):
    pass


def f():
    time.sleep(0.001)


def g():
    time.sleep(0.001)
    raise MockError()


async def test_on_raised_while_pulling():
    async def pull():
        raise MockError()

    run_no = 1
    nextline = Nextline(statement=f, run_no_start_from=run_no, timeout_on_exit=60)
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=mock_queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await auto_mode.turn_on()
            async for state in auto_mode.subscribe_state():
                if state == 'off':
                    break

    expected = ['off', 'auto_waiting', 'auto_pulling', 'off']
    assert expected == await states


async def test_on_raised_while_running():
    async def pull():
        return g

    run_no = 1
    nextline = Nextline(statement=f, run_no_start_from=run_no, timeout_on_exit=60)
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=mock_queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await auto_mode.turn_on()
            async for state in auto_mode.subscribe_state():
                if state == 'off':
                    break

    expected = ['off', 'auto_waiting', 'auto_pulling', 'auto_running', 'off']
    assert expected == await states


async def subscribe_state(auto_mode: AutoModeStateMachine):
    return [state async for state in auto_mode.subscribe_state()]
