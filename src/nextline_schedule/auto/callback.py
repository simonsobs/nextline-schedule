import asyncio
from logging import getLogger
from typing import TYPE_CHECKING

from nextline import Nextline
from nextline.plugin.spec import Context, hookimpl

from .state_machine.machine import AutoModeStateMachine

if TYPE_CHECKING:
    from .auto_mode import PullFrom


def build_state_machine(
    nextline: Nextline, callback: 'Callback'
) -> AutoModeStateMachine:
    machine = AutoModeStateMachine(callback=callback)
    callback.machine = machine
    plugin = ScheduleAutoMode(machine=machine)
    nextline.register(plugin)
    return machine


class ScheduleAutoMode:
    '''A plugin for Nextline.

    The name of this class appears as the plugin name in the log.
    '''

    def __init__(self, machine: AutoModeStateMachine):
        self._machine = machine

    @hookimpl
    async def on_initialize_run(self) -> None:
        await self._machine.on_initialized()  # type: ignore

    @hookimpl
    async def on_finished(self, context: Context) -> None:
        nextline = context.nextline
        if nextline.format_exception():
            await self._machine.on_raised()  # type: ignore
            return
        await self._machine.on_finished()  # type: ignore


class Callback:
    def __init__(self, nextline: Nextline, pull_from: 'PullFrom'):
        self._nextline = nextline
        self._pull = pull_from
        self._logger = getLogger(__name__)
        self.machine: AutoModeStateMachine  # to be set

    async def wait(self) -> None:
        match self._nextline.state:
            case 'initialized':
                await self.machine.on_initialized()  # type: ignore
            case 'finished':
                await self.machine.on_finished()  # type: ignore

    async def pull(self) -> None:
        try:
            try:
                statement = await self._pull()
            except Exception:
                self._logger.exception('')
                await self.machine.on_raised()  # type: ignore
                return
            await self._nextline.reset(statement=statement)
            await self.machine.run()  # type: ignore
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.pull() cancelled')

    async def run(self, started: asyncio.Event) -> None:
        try:
            await self._nextline.run_continue_and_wait(started)
        except asyncio.CancelledError:
            self._logger.info(f'{self.__class__.__name__}.run() cancelled')
