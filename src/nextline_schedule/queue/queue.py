import dataclasses
import datetime
from collections import deque
from collections.abc import Iterable
from typing import Optional


@dataclasses.dataclass
class QueueItem:
    name: str
    created_at: datetime.datetime
    script: str


class Queue:
    def __init__(self, items: Optional[Iterable[QueueItem]] = None):
        self.items = deque(items or [])
