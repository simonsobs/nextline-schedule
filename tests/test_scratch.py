import asyncio
from collections.abc import AsyncIterator, Iterable
from typing import TypeVar

import pytest

T = TypeVar('T')


async def aiterable(iterable: Iterable[T]) -> AsyncIterator[T]:
    '''Wrap iterable so can be used with "async for"'''
    for i in iterable:
        await asyncio.sleep(0)  # let other tasks run
        yield i


async def test_aiter__() -> None:
    agen = (i async for i in aiterable(range(5)))
    iter = agen.__aiter__()
    assert await iter.__anext__() == 0
    assert await iter.__anext__() == 1
    assert await iter.__anext__() == 2
    assert await iter.__anext__() == 3
    assert await iter.__anext__() == 4
    with pytest.raises(StopAsyncIteration):
        await iter.__anext__()


async def test_aiter() -> None:
    agen = (i async for i in aiterable(range(5)))
    iter = aiter(agen)
    assert await anext(iter) == 0
    assert await anext(iter) == 1
    assert await anext(iter) == 2
    assert await anext(iter) == 3
    assert await anext(iter) == 4
    with pytest.raises(StopAsyncIteration):
        await anext(iter)
