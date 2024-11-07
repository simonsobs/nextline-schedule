from strawberry.types import ExecutionResult

from nextline import Nextline
from nextline_schedule.auto import AutoMode
from nextline_schedule.graphql import QUERY_AUTO_MODE_MODE
from tests.auto.funcs import STATEMENT_TEMPLATE, pull_func_factory
from tests.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    statement = STATEMENT_TEMPLATE.format(name='init', count=1)
    nextline = Nextline(statement=statement)
    scheduler = pull_func_factory('schedule')
    queue = pull_func_factory('queue')
    auto_mode = AutoMode(nextline=nextline, scheduler=scheduler, queue=queue)
    context_auto_mode = {'auto_mode': auto_mode}
    context = {'schedule': context_auto_mode}
    resp = await schema.execute(QUERY_AUTO_MODE_MODE, context_value=context)
    assert isinstance(resp, ExecutionResult)
    assert resp.data
    assert resp.data['schedule']['autoMode']['mode'] == auto_mode.mode
