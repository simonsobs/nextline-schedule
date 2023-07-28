import asyncio
from logging import getLogger
from typing import Any, Callable, Coroutine

from nextline import Nextline

from nextline_schedule.types import Statement

from .machine import AutoModeStateMachine


def build_auto_mode_state_machine(
    nextline: Nextline,
    request_statement: Callable[[], Coroutine[Any, Any, Statement]],
) -> AutoModeStateMachine:
    callback = Callback(nextline=nextline, request_statement=request_statement)
    machine = AutoModeStateMachine(callback=callback)
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

        self.auto_mode: AutoModeStateMachine  # to be set

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
            try:
                statement = await self._request_statement()
            except Exception:
                self._logger.exception('')
                await self.auto_mode.on_raised()  # type: ignore
                return
            await self._nextline.reset(statement=statement)
            await self.auto_mode.run()  # type: ignore
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.pull() cancelled')

    async def run(self, started: asyncio.Event) -> None:
        try:
            await self._nextline.run_continue_and_wait(started)
            if self._nextline.exception() is not None:
                await self.auto_mode.on_raised()  # type: ignore
                return
            await self.auto_mode.on_finished()  # type: ignore
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.run() cancelled')
