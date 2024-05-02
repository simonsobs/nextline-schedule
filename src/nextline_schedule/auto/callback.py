import asyncio
from collections.abc import AsyncIterator
from logging import getLogger
from typing import Any, Callable, Coroutine

from nextline import Nextline
from nextline.plugin.spec import Context, hookimpl

from nextline_schedule.types import Statement

from .state_machine.machine import AutoModeStateMachine


class AutoMode:
    def __init__(
        self,
        nextline: Nextline,
        request_statement: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._machine = build_state_machine(
            nextline=nextline, request_statement=request_statement
        )
        on_call = OnCall(auto_mode=self._machine)
        nextline.register(on_call)

    @property
    def state(self) -> str:
        return self._machine.state

    def subscribe_state(self) -> AsyncIterator[str]:
        return self._machine.subscribe_state()

    async def turn_on(self) -> None:
        await self._machine.turn_on()  # type: ignore

    async def turn_off(self) -> None:
        await self._machine.turn_off()  # type: ignore

    async def __aenter__(self) -> 'AutoMode':
        await self._machine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._machine.__aexit__(exc_type, exc_value, traceback)


def build_state_machine(
    nextline: Nextline,
    request_statement: Callable[[], Coroutine[Any, Any, Statement]],
) -> AutoModeStateMachine:
    callback = Callback(nextline=nextline, request_statement=request_statement)
    machine = AutoModeStateMachine(callback=callback)
    callback.auto_mode = machine
    return machine


class OnCall:
    def __init__(self, auto_mode: AutoModeStateMachine):
        self.auto_mode = auto_mode

    @hookimpl
    async def on_initialize_run(self) -> None:
        await self.auto_mode.on_initialized()  # type: ignore

    @hookimpl
    async def on_finished(self, context: Context) -> None:
        nextline = context.nextline
        if nextline.format_exception():
            await self.auto_mode.on_raised()  # type: ignore
            return
        await self.auto_mode.on_finished()  # type: ignore


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
        match self._nextline.state:
            case 'initialized':
                await self.auto_mode.on_initialized()  # type: ignore
            case 'finished':
                await self.auto_mode.on_finished()  # type: ignore

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
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.run() cancelled')
