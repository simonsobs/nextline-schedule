from collections.abc import Mapping, MutableMapping
from logging import getLogger
from pathlib import Path
from typing import Optional

from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextlinegraphql.hook import spec

from .__about__ import __version__
from .auto import AutoMode
from .dummy import DummyRequestStatement
from .queue import Queue
from .scheduler import Scheduler
from .schema import Mutation, Query, Subscription

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (
    Validator("SCHEDULE.API", must_exist=True, is_type_of=str),
    Validator("SCHEDULE.LENGTH_MINUTES", must_exist=True, is_type_of=int),
    Validator("SCHEDULE.POLICY", must_exist=True, is_type_of=str),
)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        logger = getLogger(__name__)
        logger.info(f'{__package__} version: {__version__}')
        api_rul = settings.schedule.api
        length_minutes = settings.schedule.length_minutes
        policy = settings.schedule.policy

        self._dummy = DummyRequestStatement()
        self._scheduler = Scheduler(
            api_url=api_rul, length_minutes=length_minutes, policy=policy
        )
        # self._scheduler = self._dummy

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        nextline = context['nextline']
        self._queue = Queue()
        self._auto_mode = AutoMode(
            nextline=nextline, scheduler=self._scheduler, queue=self._queue
        )
        async with self._queue, self._auto_mode as y:
            yield y

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        schedule = {
            'auto_mode': self._auto_mode,
            'scheduler': self._scheduler,
            'queue': self._queue,
        }
        context['schedule'] = schedule
