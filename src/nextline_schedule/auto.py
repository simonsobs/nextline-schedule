import asyncio
from typing import Any, AsyncIterator, Callable, Coroutine, Set

from nextline import Nextline
from nextline.utils import pubsub

from nextline_schedule.fsm import build_state_machine


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
        request_statement: Callable[[], Coroutine[Any, Any, str]],
    ):
        self._nextline = nextline
        self._request_statement = request_statement
        self._tasks: Set[asyncio.Task] = set()
        self._pubsub_state = pubsub.PubSubItem[str]()

        machine = build_state_machine(self)
        machine.after_state_change = self.after_state_change.__name__  # type: ignore

    def subscribe_state(self) -> AsyncIterator[str]:
        return self._pubsub_state.subscribe()

    async def on_enter_waiting(self) -> None:
        async def wait() -> None:
            async for state in self._nextline.subscribe_state():
                if state == 'initialized':
                    await self.on_initialized()  # type: ignore
                    break
                if state == 'finished':
                    await self.on_finished()  # type: ignore
                    break
            return

        task = asyncio.create_task(wait())
        self._tasks.add(task)

    async def on_enter_auto_pulling(self) -> None:
        async def pull() -> None:
            statement = await self._request_statement()
            await self._nextline.reset(statement=statement)
            await self.run()  # type: ignore

        task = asyncio.create_task(pull())
        self._tasks.add(task)

    async def on_enter_auto_running(self) -> None:
        async def run() -> None:
            async def run_and_wait() -> None:
                async with self._nextline.run_session():
                    pass
                if self._nextline.exception() is not None:
                    await self.on_raised()  # type: ignore
                else:
                    await self.on_finished()  # type: ignore

            async def continue_on_prompt(nextline: Nextline) -> None:
                async for prompt_info in nextline.subscribe_prompt_info():
                    if prompt_info.trace_call_end:  # TODO: remove when unnecessary
                        continue
                    if not prompt_info.open:
                        continue
                    break
                await nextline.send_pdb_command(
                    command='continue',
                    prompt_no=prompt_info.prompt_no,
                    trace_no=prompt_info.trace_no,
                )

            await asyncio.gather(
                run_and_wait(),
                continue_on_prompt(self._nextline),
                # monitor(),
            )

        task = asyncio.create_task(run())
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
