from __future__ import annotations

import datetime

from fastapi_users import schemas
from fastapi_users.db import SQLAlchemyBaseUserTable
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from pydantic import BaseModel
from pydantic import SecretStr
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import func
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
    research_group_id: int | None = 0


class UserUpdate(schemas.BaseUserUpdate):
    is_researcher: bool | None = None
    full_data_access: bool | None = None
    research_group_id: int | None = None

    def create_update_dict(self):
        """Exclude admin-managed fields from self-service user updates."""
        update_dict = super().create_update_dict()
        for field in ("is_researcher", "full_data_access", "research_group_id"):
            update_dict.pop(field, None)
        return update_dict


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    last_seen_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        server_default=func.now(),
        nullable=False,
    )

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
        )


class SessionInfo(BaseModel):
    idle_expires_at: datetime.datetime
    absolute_expires_at: datetime.datetime
    warning_seconds: int


class SessionReauthentication(BaseModel):
    password: SecretStr
