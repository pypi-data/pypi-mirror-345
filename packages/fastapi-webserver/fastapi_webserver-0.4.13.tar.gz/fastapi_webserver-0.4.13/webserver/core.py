from contextlib import asynccontextmanager
from typing import Annotated, Optional

from commons.database import FileDatabaseMigrationExecutor, DatabaseAdapter
from commons.database.cache import Cache
from commons.locales import Locale, LocaleSettings
from fastapi import FastAPI, Depends, Header
from fastapi.routing import APIRoute

from webserver.config import settings


def generate_unique_route_id(route: APIRoute) -> str:
    """
    Generate a unique ID for the client side generation.
    Source: https://fastapi.tiangolo.com/advanced/generate-clients/#custom-operation-ids-and-better-method-names
    :return: route id
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    else:
        return f"{route.name}"

def _setup_databases():
    from commons import runtime
    from sqlmodel import SQLModel, inspect

    # create only the cache table on cache db
    if not inspect(settings.cache_database_adapter.engine()).has_table("cache"):
        runtime.import_module("commons.database.cache")
        SQLModel.metadata.tables["cache"].create(settings.cache_database_adapter.engine())

    # Create DB and Tables via ORM
    if settings.has_database:
        SQLModel.metadata.create_all(settings.database_adapter.engine())
        # Migrate data
        with settings.database_adapter.session() as s:
            FileDatabaseMigrationExecutor(path=settings.resources_folder / "migrations", session=s).run()
            s.close()

@asynccontextmanager
async def fastapi_lifespan(app: FastAPI):
    from commons import runtime
    """Manages the lifespan of a FastAPI application."""

    # --- FastAPI app startup
    # Load modules to allow orm metadada creation
    runtime.import_modules(settings.MODULES)
    _setup_databases()
    # --- FastAPI app execution
    yield
    # --- FastAPI app shutdown

# --- Dependencies
async def _get_locale_config() -> Optional[LocaleSettings]:
    return settings.locale_config

ServerDatabase = Annotated[DatabaseAdapter, Depends(lambda: settings.database_adapter)]
ServerCache = Annotated[Cache, Depends(lambda: Cache(database=settings.cache_database_adapter))]
LocaleSettings = Annotated[LocaleSettings, Depends(_get_locale_config)]

async def _lookup_lang(accept_language: Annotated[str, Header()], locale_config: LocaleSettings) -> Optional[Locale]:
    from webserver.http import headers
    return headers.get_locale(accept_language, locale_config)

AvailableLocale = Annotated[Optional[Locale], Depends(_lookup_lang)]
