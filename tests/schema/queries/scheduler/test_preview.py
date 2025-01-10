from unittest.mock import AsyncMock

from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.graphql import QUERY_SCHEDULER_PREVIEW
from nextline_test_utils.strategies import st_python_scripts
from tests.schema.conftest import Schema


@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    script = d.draw(st_python_scripts())
    scheduler = AsyncMock(return_value=script)

    context = {'schedule': {'scheduler': scheduler}}
    resp = await schema.execute(QUERY_SCHEDULER_PREVIEW, context_value=context)
    assert (data := resp.data)

    expected = {
        'schedule': {
            'scheduler': {
                'preview': {
                    'script': script,
                }
            }
        }
    }
    assert data == expected
