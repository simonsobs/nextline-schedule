import asyncio
import time
from collections.abc import Callable

from nextline import Nextline
from nextline_schedule.auto import AutoMode

from .funcs import pull_func_factory


def f() -> None:  # pragma: no cover
    time.sleep(0.001)


async def pull() -> Callable[[], None]:  # pragma: no cover
    return f


async def test_turn_off_while_waiting() -> None:
    nextline = Nextline(
        statement=f,
        trace_threads=True,
        trace_modules=True,
        timeout_on_exit=60,
    )
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=pull, queue=queue)

    states = asyncio.create_task(subscribe_state(auto_mode))

    async with auto_mode:
        async with nextline:
            await nextline.run()
            async for prompt in nextline.prompts():  # pragma: no branch
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
