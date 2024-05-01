import dataclasses
import itertools
from collections import deque
from collections.abc import Iterable
from datetime import datetime
from typing import Optional


@dataclasses.dataclass
class QueueItem:
    id: int
    name: str
    created_at: datetime
    script: str


@dataclasses.dataclass
class PushArg:
    name: str
    script: str

    def to_queue_item(self, id: int) -> QueueItem:
        return QueueItem(
            id=id,
            name=self.name,
            created_at=datetime.utcnow(),
            script=self.script,
        )


class Queue:
    def __init__(self, items: Optional[Iterable[QueueItem]] = None):
        items = list(items or [])
        id_start = max(i.id for i in items) + 1 if items else 0
        self._id_counter = itertools.count(id_start).__next__
        self.items = deque(items)
        self._map = {i.id: i for i in items}

    def __len__(self) -> int:
        return len(self.items)

    def push(self, arg: PushArg) -> QueueItem:
        item = arg.to_queue_item(id=self._id_counter())
        self.items.append(item)
        self._map[item.id] = item
        return item

    def pop(self) -> QueueItem | None:
        try:
            item = self.items.popleft()
            del self._map[item.id]
            return item
        except IndexError:
            return None

    def remove(self, id: int) -> bool:
        item = self._map.get(id)
        if item is None:
            return False
        self.items.remove(item)
        del self._map[id]
        return True
