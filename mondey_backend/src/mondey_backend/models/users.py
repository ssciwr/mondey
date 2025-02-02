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
    full_data_access: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    research_group_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class UserRead(schemas.BaseUser[int]):
    is_researcher: bool
    full_data_access: bool
    research_group_id: int


class UserCreate(schemas.BaseUserCreate):
    is_researcher: bool | None = False
    full_data_access: bool | None = False
    research_group_id: int | None = 0


class UserUpdate(schemas.BaseUserUpdate):
    is_researcher: bool | None = None
    full_data_access: bool | None = None
    research_group_id: int | None = None


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
        )
