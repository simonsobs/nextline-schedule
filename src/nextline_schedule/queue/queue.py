from collections.abc import AsyncIterator, Iterable
from logging import getLogger
from typing import Optional

from nextline.utils import pubsub

from .item import PushArg, QueueItem
from .queue_imp import QueueImp


class QueueEmpty(Exception):
    pass


class Queue:
    def __init__(self, items: Optional[Iterable[QueueItem]] = None):
        self._pubsub = pubsub.PubSubItem[list[QueueItem]]()
        self._queue = QueueImp(items)
        self._logger = getLogger(__name__)

    async def __call__(self) -> str:
        item = await self.pop()
        if item is None:
            self._logger.info('Queue is empty')
            raise QueueEmpty
        return item.script

    @property
    def items(self):
        return self._pubsub.latest()

    def subscribe(self) -> AsyncIterator[list[QueueItem]]:
        return self._pubsub.subscribe()

    def __len__(self) -> int:
        return len(self._queue)

    async def push(self, arg: PushArg) -> QueueItem:
        item = self._queue.push(arg)
        await self._pubsub.publish(list(self._queue.items))
        return item

    async def pop(self) -> QueueItem | None:
        item = self._queue.pop()
        if item is None:
            return None
        await self._pubsub.publish(list(self._queue.items))
        return item

    async def remove(self, id: int) -> bool:
        if not self._queue.remove(id):
            return False
        await self._pubsub.publish(list(self._queue.items))
        return True

    async def move_to_first(self, id: int) -> bool:
        if not self._queue.move_to_first(id):
            return False
        await self._pubsub.publish(list(self._queue.items))
        return True

    async def move_to_last(self, id: int) -> bool:
        if not self._queue.move_to_last(id):
            return False
        await self._pubsub.publish(list(self._queue.items))
        return True

    async def move_one_forward(self, id: int) -> bool:
        if not self._queue.move_one_forward(id):
            return False
        await self._pubsub.publish(list(self._queue.items))
        return True

    async def move_one_backward(self, id: int) -> bool:
        if not self._queue.move_one_backward(id):
            return False
        await self._pubsub.publish(list(self._queue.items))
        return True

    async def aclose(self) -> None:
        await self._pubsub.aclose()

    async def __aenter__(self) -> 'Queue':
        await self._pubsub.publish(list(self._queue.items))
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.aclose()
