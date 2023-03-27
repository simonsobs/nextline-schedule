import asyncio
from typing import AsyncIterator, Protocol, Set

from nextline.utils import pubsub

from nextline_schedule.fsm import build_state_machine


class CallbackType(Protocol):
    async def wait(self) -> None:
        ...

    async def pull(self) -> None:
        ...

    async def run(self) -> None:
        ...


class AutoMode:
    '''A model of the finite state machine.'''

    def __init__(self, callback: CallbackType):
        self._callback = callback
        self._tasks: Set[asyncio.Task] = set()
        self._pubsub_state = pubsub.PubSubItem[str]()

        machine = build_state_machine(self)
        machine.after_state_change = self.after_state_change.__name__  # type: ignore

    def subscribe_state(self) -> AsyncIterator[str]:
        return self._pubsub_state.subscribe()

    async def on_enter_waiting(self) -> None:
        task = asyncio.create_task(self._callback.wait())
        self._tasks.add(task)

    async def on_enter_auto_pulling(self) -> None:
        task = asyncio.create_task(self._callback.pull())
        self._tasks.add(task)

    async def on_enter_auto_running(self) -> None:
        task = asyncio.create_task(self._callback.run())
        self._tasks.add(task)

    async def after_state_change(self) -> None:
        await self._collect_tasks()
        await self._pubsub_state.publish(self.state)  # type: ignore

    async def _collect_tasks(self) -> None:
        if not self._tasks:
            return
        done, _ = await asyncio.wait(
            self._tasks, timeout=0, return_when=asyncio.FIRST_COMPLETED
        )
        self._tasks -= done

    async def close(self) -> None:
        await self._collect_tasks()
        await self._pubsub_state.close()

    async def __aenter__(self) -> 'AutoMode':
        await self.start()  # type: ignore
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        await self.close()
