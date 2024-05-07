from typing import Any, Callable, Coroutine

from nextline_schedule.types import Statement

PullFunc = Callable[[], Coroutine[Any, Any, Statement]]
