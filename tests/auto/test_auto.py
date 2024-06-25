import asyncio

from nextline import Nextline
from nextline.events import OnStartRun
from nextline.plugin.spec import hookimpl

from nextline_schedule.auto import AutoMode

STATEMENT_SCHEDULER = '''
"""run_no: {run_no}"""
import time
time.sleep(0.01)
'''

STATEMENT_QUEUE = '''
"""queue"""
import time
time.sleep(0.01)
'''


class MockScheduler:
    def __init__(self, nextline: Nextline):
        self._nextline = nextline

    async def __call__(self) -> str:
        return STATEMENT_SCHEDULER.format(run_no=self._nextline.run_no + 1)


async def mock_queue() -> str:
    return STATEMENT_QUEUE


class TurnOffAtRunThree:
    def __init__(self, auto_mode: AutoMode, done: asyncio.Event) -> None:
        self._auto_mode = auto_mode
        self._done = done

    @hookimpl
    async def on_start_run(self, event: OnStartRun) -> None:
        await self._turn_off_if_run_3(event)

    async def _turn_off_if_run_3(self, event: OnStartRun) -> None:
        if not event.run_no == 3:
            return
        await self._auto_mode.turn_off()
        self._done.set()


async def test_one() -> None:
    run_no = 1
    statement = STATEMENT_SCHEDULER.format(run_no=run_no)
    nextline = Nextline(statement=statement, run_no_start_from=run_no)
    scheduler = MockScheduler(nextline=nextline)
    auto_mode = AutoMode(nextline=nextline, scheduler=scheduler, queue=mock_queue)
    done = asyncio.Event()
    nextline.register(TurnOffAtRunThree(auto_mode, done))

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            assert auto_mode.state == 'off'
            await auto_mode.turn_on()
            await done.wait()

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


async def subscribe_state(auto_mode: AutoMode):
    return [state async for state in auto_mode.subscribe_state()]
