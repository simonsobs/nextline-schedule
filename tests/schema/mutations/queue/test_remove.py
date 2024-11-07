from unittest.mock import Mock

from deepdiff import DeepDiff
from hypothesis import given
from hypothesis import strategies as st

from nextline_schedule.graphql import MUTATE_QUEUE_REMOVE
from nextline_schedule.queue import Queue
from nextline_test_utils.strategies import st_graphql_ints
from tests.schema.conftest import Schema


@given(d=st.data())
async def test_schema(d: st.DataObject, schema: Schema) -> None:
    id = d.draw(st_graphql_ints(min_value=1))
    return_value = d.draw(st.booleans())

    queue = Mock(spec=Queue)
    queue.remove.return_value = return_value

    context_values = {'schedule': {'queue': queue}}
    variable_values = {'id': id}

    resp = await schema.execute(
        MUTATE_QUEUE_REMOVE,
        context_value=context_values,
        variable_values=variable_values,
    )

    assert (data := resp.data)
    expected_data = {'schedule': {'queue': {'remove': return_value}}}
    assert DeepDiff(data, expected_data) == {}

    queue.remove.assert_called_once_with(id)
