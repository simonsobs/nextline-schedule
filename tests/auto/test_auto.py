import asyncio

from nextline import Nextline
from nextline_schedule.auto import AutoMode

from .funcs import STATEMENT_TEMPLATE, pull_func_factory, until_state


async def test_one() -> None:
    statement = STATEMENT_TEMPLATE.format(name='init', count=1)
    nextline = Nextline(statement=statement)
    scheduler = pull_func_factory('schedule')
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=scheduler, queue=queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            assert auto_mode.state == 'off'
            await auto_mode.turn_on()
            await asyncio.sleep(0.0001)
            await until_state(nextline, state='running', count=2)
            await asyncio.sleep(0.0001)
            await auto_mode.turn_off()

    expected = [
        'off',
        'auto_waiting',
        'auto_pulling',
        'auto_running',
        'auto_pulling',
        'auto_running',
        'off',
    ]
    assert expected == await states


async def subscribe_state(auto_mode: AutoMode) -> list[str]:
    return [state async for state in auto_mode.subscribe_state()]
