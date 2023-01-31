from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Tuple

from dynaconf import Dynaconf, Validator
from nextline import Nextline
from nextlinegraphql.custom.decorator import asynccontextmanager
from nextlinegraphql.hook import spec

from .auto import AutoMode
from .funcs import generate_statement
from .schema import Mutation, Query, Subscription

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (Validator("SCHEDULE.API", must_exist=True, is_type_of=str),)


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
        pass

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        nextline = context['nextline']
        request_statement = RequestStatement(nextline=nextline)
        self._auto_mode = AutoMode(
            nextline=nextline, request_statement=request_statement
        )
        async with self._auto_mode as y:
            yield y

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['auto_mode'] = self._auto_mode


class RequestStatement:
    def __init__(self, nextline: Nextline):
        self._nextline = nextline

    async def __call__(self) -> str:
        return generate_statement(run_no=self._nextline.run_no + 1)
