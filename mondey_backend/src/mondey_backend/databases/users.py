from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.pool import StaticPool

from ..models.users import AccessToken
from ..models.users import Base
from ..models.users import User
from ..settings import app_settings

engine_path = (
    f"/{app_settings.DATABASE_PATH}/users.db" if app_settings.DATABASE_PATH else ""
)
engine = create_async_engine(
    f"sqlite+aiosqlite://{engine_path}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_user_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: Annotated[AsyncSession, Depends(get_async_session)]):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
