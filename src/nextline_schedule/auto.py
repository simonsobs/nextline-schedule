import asyncio
from typing import Any, AsyncIterator, Callable, Coroutine, Set

from nextline import Nextline
from nextline.utils import pubsub

from nextline_schedule.fsm import build_state_machine
from nextline_schedule.types import Statement


class Callback:
    def __init__(
        self,
        auto_mode: 'AutoMode',
        nextline: Nextline,
        request_statement: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._auto_mode = auto_mode
        self._nextline = nextline
        self._request_statement = request_statement

    async def wait(self) -> None:
        async for state in self._nextline.subscribe_state():
            if state == 'initialized':
                await self._auto_mode.on_initialized()  # type: ignore
                break
            if state == 'finished':
                await self._auto_mode.on_finished()  # type: ignore
                break
        return

    async def pull(self) -> None:
        statement = await self._request_statement()
        await self._nextline.reset(statement=statement)
        await self._auto_mode.run()  # type: ignore

    async def run(self) -> None:
        async with self._nextline.run_session():
            async for prompt in self._nextline.prompts():
                await self._nextline.send_pdb_command(
                    command='continue',
                    prompt_no=prompt.prompt_no,
                    trace_no=prompt.trace_no,
                )
        if self._nextline.exception() is not None:
            await self._auto_mode.on_raised()  # type: ignore
            return
        await self._auto_mode.on_finished()  # type: ignore


class AutoMode:
    '''A model of the finite state machine.

    >>> nextline = Nextline(statement='')
    >>> async def request_statement() -> str:
    ...     return ''

    >>> auto_mode = AutoMode(nextline=nextline, request_statement=request_statement)
    >>> auto_mode.state
    'created'
    '''

    def __init__(
        self,
        nextline: Nextline,
        request_statement: Callable[[], Coroutine[Any, Any, Statement]],
    ):
        self._callback = Callback(self, nextline, request_statement)
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
