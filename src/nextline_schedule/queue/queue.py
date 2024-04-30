import dataclasses
from collections import deque
from collections.abc import Iterable
from datetime import datetime
from typing import Optional


@dataclasses.dataclass
class QueueItem:
    name: str
    created_at: datetime
    script: str


@dataclasses.dataclass
class PushArg:
    name: str
    script: str

    def to_queue_item(self) -> QueueItem:
        return QueueItem(
            name=self.name,
            created_at=datetime.utcnow(),
            script=self.script,
        )


class Queue:
    def __init__(self, items: Optional[Iterable[QueueItem]] = None):
        self.items = deque(items or [])

    def __len__(self) -> int:
        return len(self.items)

    def push(self, arg: PushArg) -> QueueItem:
        item = arg.to_queue_item()
        self.items.append(item)
        return item
