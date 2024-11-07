from typing import TypedDict
from unittest.mock import AsyncMock

from deepdiff import DeepDiff
from hypothesis import given
from hypothesis import strategies as st

from nextline import Nextline
from nextline_schedule.graphql import MUTATE_SCHEDULER_LOAD_SCRIPT
from nextline_schedule.scheduler import Scheduler
from nextline_test_utils.strategies import st_python_scripts
from tests.schema.conftest import Schema


class Input(TypedDict):
    apiUrl: str | None
    lengthMinutes: int | None
    policy: str | None


@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    init_statement = d.draw(st_python_scripts())
    statement = d.draw(st_python_scripts())

    nextline = Nextline(statement=init_statement)

    scheduler = AsyncMock(spec=Scheduler)
    scheduler.return_value = statement

    async with nextline:
        context_values = {'nextline': nextline, 'schedule': {'scheduler': scheduler}}
        variable_values = {'input': input}

        resp = await schema.execute(
            MUTATE_SCHEDULER_LOAD_SCRIPT,
            context_value=context_values,
            variable_values=variable_values,
        )

        assert (data := resp.data)
        expected_data = {'schedule': {'scheduler': {'loadScript': True}}}
        assert DeepDiff(data, expected_data) == {}

        scheduler.assert_awaited_once()
        assert statement == nextline.statement
