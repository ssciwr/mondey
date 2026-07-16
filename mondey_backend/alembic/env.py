from __future__ import annotations

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlmodel import SQLModel

from alembic import context
from mondey_backend.databases.mondey import engine as mondey_engine
from mondey_backend.databases.users import engine as async_users_engine
from mondey_backend.models.children import *
from mondey_backend.models.milestones import *
from mondey_backend.models.questions import *
from mondey_backend.models.research import *
from mondey_backend.models.users import Base as UsersBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alembic.env")

TARGET_METADATA = {
    "mondey": SQLModel.metadata,
    "users": UsersBase.metadata,
}


def users_sync_url() -> URL:
    # Keep the URL object: stringifying it masks the password as ``***``.
    url = async_users_engine.url
    if url.drivername == "sqlite+aiosqlite":
        url = url.set(drivername="sqlite")
    return url


def run_migrations() -> None:
    engines = {
        "mondey": mondey_engine,
        "users": create_engine(users_sync_url()),
    }
    try:
        for name, engine in engines.items():
            with engine.connect() as connection:
                logger.info("Migrating %s database", name)
                context.configure(
                    connection=connection,
                    target_metadata=TARGET_METADATA[name],
                    upgrade_token=f"{name}_upgrades",
                )
                with context.begin_transaction():
                    context.run_migrations(engine_name=name)
    finally:
        engines["users"].dispose()


run_migrations()
