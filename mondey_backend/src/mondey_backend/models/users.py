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
from sqlmodel import Field
from sqlmodel import SQLModel


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
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


class Observer(SQLModel, table=True):
    user_id: int = Field(default=None, primary_key=True)
    year_of_birth: str = Field(max_length=255, nullable=False)
    gender: str = Field(max_length=255, nullable=False)
    education: str = Field(max_length=255, nullable=False)
    working_hours: str = Field(max_length=255, nullable=False)
    income_per_year: str = Field(max_length=255, nullable=False)
    profession: str = Field(max_length=255, nullable=False)


# class Observer(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     yearOfBirth: str
#     gender: str
#     education: str
#     workingHours: str
#     incomePerYear: str
#     profession: str
