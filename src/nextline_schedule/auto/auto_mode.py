import dataclasses
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Literal

from nextline import Nextline
from nextline.utils import pubsub

from nextline_schedule.types import Statement

from .callback import Callback, build_state_machine
from .types import PullFunc

FromName = Literal['scheduler', 'queue']
ModeName = Literal['off', 'scheduler', 'queue']


class AutoMode:
    def __init__(self, nextline: Nextline, scheduler: PullFunc, queue: PullFunc):
        self._pull_from = PullFrom(
            scheduler=scheduler, queue=queue, on_from_changed=self.on_from_changed
        )
        callback = Callback(
            nextline=nextline,
            pull_func=self._pull_from,
            on_state_changed=self.on_state_changed,
        )
        self._machine = build_state_machine(nextline=nextline, callback=callback)
        self._mode: ModeName = 'off'
        self._pubsub_mode = pubsub.PubSubItem[ModeName]()

    @property
    def state(self) -> str:
        return self._machine.state

    def subscribe_state(self) -> AsyncIterator[str]:
        return self._machine.subscribe_state()

    @property
    def mode(self) -> ModeName:
        return self._mode

    def subscribe_mode(self) -> AsyncIterator[ModeName]:
        return self._pubsub_mode.subscribe()

    async def change_mode(self, mode: ModeName) -> None:
        if mode == 'off':
            await self._machine.turn_off()  # type: ignore
            return
        await self._pull_from.change_from(mode)
        await self._machine.turn_on()  # type: ignore

    async def turn_on(self) -> None:
        await self._machine.turn_on()  # type: ignore

    async def turn_off(self) -> None:
        await self._machine.turn_off()  # type: ignore

    async def __aenter__(self) -> 'AutoMode':
        await self._pubsub_mode.publish(self._mode)
        await self._machine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._machine.__aexit__(exc_type, exc_value, traceback)
        await self._pubsub_mode.aclose()

    async def on_state_changed(self, state: str) -> None:
        if state == 'off':
            if self._mode == 'off':
                return
            self._mode = 'off'
            await self._pubsub_mode.publish(self._mode)
            return

        if state.startswith('auto_'):
            from_ = self._pull_from.current
            if self._mode == from_:
                return
            self._mode = from_
            await self._pubsub_mode.publish(self._mode)

    async def on_from_changed(self, name: FromName) -> None:
        if self.state == 'off':
            return

        if self._mode == name:
            return
        self._mode = name
        await self._pubsub_mode.publish(self._mode)


@dataclasses.dataclass
class PullFromItem:
    name: FromName
    pull: PullFunc


class PullFrom:
    def __init__(
        self,
        scheduler: PullFunc,
        queue: PullFunc,
        on_from_changed: Callable[[FromName], Awaitable[None]],
    ):
        self._scheduler = PullFromItem(name='scheduler', pull=scheduler)
        self._queue = PullFromItem(name='queue', pull=queue)
        self._on_from_changed = on_from_changed
        self._map = {
            self._scheduler.name: self._scheduler,
            self._queue.name: self._queue,
        }
        self._current = self._scheduler

    async def __call__(self) -> Statement:
        return await self._current.pull()

    async def change_from(self, name: FromName) -> None:
        old = self._current.name
        self._current = self._map[name]
        if old != self._current.name:
            await self._on_from_changed(self._current.name)

    @property
    def current(self) -> FromName:
        return self._current.name
