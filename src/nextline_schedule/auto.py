import asyncio

from nextline import Nextline

from nextline_schedule.fsm import build_state_machine
from nextline_schedule.funcs import generate_statement


class AutoMode:
    '''A model of the finite state machine.

    >>> auto_mode = AutoMode(nextline=Nextline(statement=''))
    >>> auto_mode.state
    'off'
    '''

    def __init__(self, nextline: Nextline):
        self._nextline = nextline
        machine = build_state_machine(self)
        machine.after_state_change = self.after_state_change.__name__  # type: ignore

    async def after_state_change(self) -> None:
        print(f'after_state_change: {self.state}')  # type: ignore

    async def on_enter_auto_pulling(self) -> None:
        print('on_enter_auto_pulling')
        statement = await generate_statement(self._nextline.run_no + 1)
        print(statement)
        await self._nextline.reset(statement=statement)
        await self.run()  # type: ignore

    async def on_enter_auto_running(self) -> None:
        print('on_enter_auto_running')
        await asyncio.gather(self._nextline.run(), self.continue_on_prompt())
        print('there')

    async def continue_on_prompt(self) -> None:
        async for prompt_info in self._nextline.subscribe_prompt_info():
            if prompt_info.trace_call_end:  # TODO: remove when unnecessary
                continue
            if not prompt_info.open:
                continue
            break
        self._nextline.send_pdb_command(
            command='continue',
            prompt_no=prompt_info.prompt_no,
            trace_no=prompt_info.trace_no,
        )

    async def monitor_nextline_states(self) -> None:
        async for state in self._nextline.subscribe_state():
            if state == 'initialized':
                await self.on_initialized()  # type: ignore
                continue
            if state == 'finished':
                await self.on_finished()  # type: ignore
                continue
        return

    async def __aenter__(self) -> 'AutoMode':
        self._monitor = asyncio.create_task(self.monitor_nextline_states())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        await self._monitor
