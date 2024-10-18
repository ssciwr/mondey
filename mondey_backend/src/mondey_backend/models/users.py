from __future__ import annotations

from fastapi_users import schemas
from fastapi_users.db import SQLAlchemyBaseUserTable
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_researcher: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class UserRead(schemas.BaseUser[int]):
    is_researcher: bool


class UserCreate(schemas.BaseUserCreate):
    is_researcher: bool | None = False


class UserUpdate(schemas.BaseUserUpdate):
    is_researcher: bool | None = None


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
        )
