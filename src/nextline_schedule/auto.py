import asyncio
from logging import getLogger
from typing import Any, Callable, Coroutine

from nextline import Nextline

from nextline_schedule.machine import Machine
from nextline_schedule.types import Statement


def build_machine(
    nextline: Nextline,
    request_statement: Callable[[], Coroutine[Any, Any, Statement]],
) -> Machine:
    callback = Callback(nextline=nextline, request_statement=request_statement)
    machine = Machine(callback=callback)
    callback.auto_mode = machine
    return machine


class Callback:
    def __init__(
        self,
        nextline: Nextline,
        request_statement: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._nextline = nextline
        self._request_statement = request_statement

        self._logger = getLogger(__name__)

        self.auto_mode: Machine  # to be set

    async def wait(self) -> None:
        try:
            async for state in self._nextline.subscribe_state():
                if state == 'initialized':
                    await self.auto_mode.on_initialized()  # type: ignore
                    break
                if state == 'finished':
                    await self.auto_mode.on_finished()  # type: ignore
                    break
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.wait() cancelled')
        return

    async def pull(self) -> None:
        try:
            statement = await self._request_statement()
        except Exception:
            self._logger.exception('')
            await self.auto_mode.on_raised()  # type: ignore
            return
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
