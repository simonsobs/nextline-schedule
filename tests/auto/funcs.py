import asyncio
from itertools import count

from nextline import Nextline
from nextline_schedule.auto.types import PullFunc

STATEMENT_TEMPLATE = '''
"""{name}: {count}"""
import time
time.sleep(0.01)
'''


def pull_func_factory(name: str) -> PullFunc:
    counter = count(1).__next__

    async def pull_func() -> str:
        await asyncio.sleep(0)
        return STATEMENT_TEMPLATE.format(name=name, count=counter())

    return pull_func


async def until_state(
    nextline: Nextline, state: str = 'finished', count: int = 1
) -> None:
    async for s in nextline.subscribe_state():  # pragma: no branch
        if s != state:
            continue
        count -= 1
        if count == 0:
            break
