from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Tuple

from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from nextlinegraphql.hook import spec

from .auto import AutoMode
from .scheduler import DummyRequestStatement, RequestStatement
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
    def dynaconf_preload(self) -> Optional[Tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[Tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[Tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        api_rul = settings.schedule.api
        length_minutes = settings.schedule.length_minutes
        policy = settings.schedule.policy

        self._request_statement = RequestStatement(
            api_url=api_rul, length_minutes=length_minutes, policy=policy
        )

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        nextline = context['nextline']
        self._auto_mode = AutoMode(
            nextline=nextline, request_statement=self._request_statement
        )
        async with self._auto_mode as y:
            yield y

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['auto_mode'] = self._auto_mode
        context['scheduler'] = self._request_statement
