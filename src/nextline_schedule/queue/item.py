import dataclasses
from datetime import datetime


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
