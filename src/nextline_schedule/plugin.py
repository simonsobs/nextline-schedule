from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Tuple

from dynaconf import Dynaconf, Validator
from nextlinegraphql.custom.decorator import asynccontextmanager
from nextlinegraphql.hook import spec
from starlette.applications import Starlette

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
    async def lifespan(self, app: Starlette, context: Mapping):
        yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        pass
