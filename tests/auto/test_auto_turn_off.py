import asyncio
import time
from collections.abc import Callable

from nextline import Nextline
from nextline_schedule.auto import AutoMode

STATEMENT_QUEUE = '''
"""queue"""
import time
time.sleep(0.01)
'''


async def mock_queue() -> str:
    return STATEMENT_QUEUE


def f() -> None:
    time.sleep(0.001)


async def pull() -> Callable[[], None]:
    return f


async def test_turn_off_while_waiting() -> None:
    run_no = 1
    nextline = Nextline(
        statement=f,
        run_no_start_from=run_no,
        trace_threads=True,
        trace_modules=True,
        timeout_on_exit=60,
    )
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=mock_queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await nextline.run()
            async for prompt in nextline.prompts():
                break
            await auto_mode.turn_on()
            await auto_mode.turn_off()
            await nextline.send_pdb_command(
                command='continue',
                prompt_no=prompt.prompt_no,
                trace_no=prompt.trace_no,
            )

    expected = ['off', 'auto_waiting', 'off']
    assert expected == await states


async def subscribe_state(auto_mode: AutoMode) -> list[str]:
    return [state async for state in auto_mode.subscribe_state()]
