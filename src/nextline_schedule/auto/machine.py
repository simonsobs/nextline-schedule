import asyncio
from logging import getLogger
from typing import AsyncIterator, Protocol, Set

from nextline.utils import pubsub

from .factory import build_state_machine


class CallbackType(Protocol):
    async def wait(self) -> None:
        ...

    async def pull(self) -> None:
        ...

    async def run(self, started: asyncio.Event) -> None:
        ...


class AutoModeStateMachine:
    '''The finite state machine for auto mode.'''

    def __init__(self, callback: CallbackType):
        self._callback = callback
        self._tasks: Set[asyncio.Task] = set()
        self._pubsub_state = pubsub.PubSubItem[str]()
        self._logger = getLogger(__name__)
        machine = build_state_machine(model=self)
        machine.after_state_change = self.after_state_change.__name__  # type: ignore

    def subscribe_state(self) -> AsyncIterator[str]:
        return self._pubsub_state.subscribe()

    async def on_enter_waiting(self) -> None:
        task = asyncio.create_task(self._callback.wait())
        self._task = task
        self._tasks.add(task)

    async def on_enter_auto_pulling(self) -> None:
        task = asyncio.create_task(self._callback.pull())
        self._task = task
        self._tasks.add(task)

    async def on_enter_auto_running(self) -> None:
        started = asyncio.Event()
        task = asyncio.create_task(self._callback.run(started=started))
        await started.wait()
        self._task = task
        self._tasks.add(task)

    async def after_state_change(self) -> None:
        await self._collect_tasks()
        await self._pubsub_state.publish(self.state)  # type: ignore

    async def cancel_task(self) -> None:
        self._task.cancel()

    async def _collect_tasks(self) -> None:
        if not self._tasks:
            return
        done, _ = await asyncio.wait(
            self._tasks,
            timeout=0,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in done:
            if (exc := task.exception()) is not None:
                self._logger.warning('An exception raised in a task', exc_info=exc)
        self._tasks -= done

    async def close(self) -> None:
        await self._collect_tasks()
        await self._pubsub_state.close()

    async def __aenter__(self) -> 'AutoModeStateMachine':
        await self.start()  # type: ignore
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        await self.close()
