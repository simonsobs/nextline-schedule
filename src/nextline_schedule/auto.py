from typing import Any, Callable, Coroutine

from nextline import Nextline

from nextline_schedule.machine import Machine
from nextline_schedule.types import Statement


def build_machine(
    nextline: Nextline,
    request_statement: Callable[[], Coroutine[Any, Any, Statement]],
) -> Machine:
    callback = Callback(nextline, request_statement)
    auto_mode = Machine(callback=callback)
    callback.auto_mode = auto_mode
    return auto_mode


class Callback:
    def __init__(
        self,
        nextline: Nextline,
        request_statement: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._nextline = nextline
        self._request_statement = request_statement

        self.auto_mode: Machine  # to be set

    async def wait(self) -> None:
        async for state in self._nextline.subscribe_state():
            if state == 'initialized':
                await self.auto_mode.on_initialized()  # type: ignore
                break
            if state == 'finished':
                await self.auto_mode.on_finished()  # type: ignore
                break
        return

    async def pull(self) -> None:
        statement = await self._request_statement()
        await self._nextline.reset(statement=statement)
        await self.auto_mode.run()  # type: ignore

    async def run(self) -> None:
        async with self._nextline.run_session():
            async for prompt in self._nextline.prompts():
                await self._nextline.send_pdb_command(
                    command='continue',
                    prompt_no=prompt.prompt_no,
                    trace_no=prompt.trace_no,
                )
        if self._nextline.exception() is not None:
            await self.auto_mode.on_raised()  # type: ignore
            return
        await self.auto_mode.on_finished()  # type: ignore
