import dataclasses
from collections.abc import AsyncIterator

from nextline import Nextline

from nextline_schedule.types import Statement

from .callback import Callback, build_state_machine
from .types import PullFunc


class AutoMode:
    def __init__(self, nextline: Nextline, scheduler: PullFunc, queue: PullFunc):
        self._pull_from = PullFrom(scheduler=scheduler, queue=queue)
        callback = Callback(nextline=nextline, pull_func=self._pull_from)
        self._machine = build_state_machine(nextline=nextline, callback=callback)

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


@dataclasses.dataclass
class PullFromItem:
    name: str
    pull: PullFunc


class PullFrom:
    def __init__(self, scheduler: PullFunc, queue: PullFunc):
        self._scheduler = PullFromItem(name='scheduler', pull=scheduler)
        self._queue = PullFromItem(name='queue', pull=queue)
        self._current = self._scheduler

    async def __call__(self) -> Statement:
        return await self._current.pull()
