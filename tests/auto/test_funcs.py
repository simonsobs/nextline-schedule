import asyncio

from hypothesis import given, settings
from hypothesis import strategies as st

from nextline import Nextline
from nextline_schedule.auto import AutoMode

from .funcs import STATEMENT_TEMPLATE, pull_func_factory, until_state


async def test_pull_func_factory() -> None:
    name = 'script'
    pull = pull_func_factory(name)

    statement = await pull()
    assert isinstance(statement, str)
    assert name in statement
    assert '1' in statement


@settings(deadline=None)
@given(data=st.data())
async def test_until_state(data: st.DataObject) -> None:
    state = data.draw(st.sampled_from(['finished', 'running']))
    count = data.draw(st.integers(min_value=1, max_value=3))

    statement = STATEMENT_TEMPLATE.format(name='init', count=1)
    nextline = Nextline(statement=statement)
    scheduler = pull_func_factory('schedule')
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=scheduler, queue=queue)

    async with auto_mode:
        async with nextline:
            await auto_mode.turn_on()
            await until_state(nextline, state=state, count=count)

            # TODO: Without the sleep, the exception
            # `asyncio.exceptions.CancelledError` is caught at
            # https://github.com/simonsobs/nextline/blob/v0.7.18/nextline/fsm/callback.py#L65
            # await asyncio.sleep(0.0001)

            await auto_mode.turn_off()
            await until_state(nextline)
