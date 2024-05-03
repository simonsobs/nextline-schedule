import asyncio

from nextline import Nextline

from nextline_schedule.auto import AutoMode

STATEMENT = '''
"""run_no: {run_no}"""
import time
time.sleep(0.01)
'''


class RequestStatement:
    def __init__(self, nextline: Nextline):
        self._nextline = nextline

    async def __call__(self) -> str:
        return STATEMENT.format(run_no=self._nextline.run_no + 1)


async def test_one() -> None:
    run_no = 1
    statement = STATEMENT.format(run_no=run_no)
    nextline = Nextline(statement=statement, run_no_start_from=run_no)
    pull = RequestStatement(nextline=nextline)
    auto_mode = AutoMode(nextline=nextline, scheduler=pull)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await control(auto_mode, nextline)

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


async def control(auto_mode: AutoMode, nextline: Nextline):
    assert auto_mode.state == 'off'  # type: ignore
    await auto_mode.turn_on()  # type: ignore
    async for run_info in nextline.subscribe_run_info():
        if run_info.run_no == 3 and run_info.state == 'running':
            break
    await auto_mode.turn_off()  # type: ignore


async def subscribe_state(auto_mode: AutoMode):
    return [state async for state in auto_mode.subscribe_state()]
