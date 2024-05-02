from collections.abc import AsyncIterator
from typing import Any, Callable, Coroutine

from nextline import Nextline

from nextline_schedule.types import Statement

from .callback import build_state_machine


class AutoMode:
    def __init__(
        self,
        nextline: Nextline,
        pull_func: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._machine = build_state_machine(nextline=nextline, pull_func=pull_func)

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
