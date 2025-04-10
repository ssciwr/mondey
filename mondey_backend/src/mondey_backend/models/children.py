from __future__ import annotations

from sqlalchemy.orm import Mapped
from sqlmodel import Field
from sqlmodel import SQLModel

from mondey_backend.src.mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.src.mondey_backend.models.utils import back_populates


class ChildBase(SQLModel):
    name: str = ""
    birth_year: int
    birth_month: int
    color: str | None = None


class Child(ChildBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    has_image: bool
    answering_sessions: Mapped[list[MilestoneAnswerSession]] = back_populates(
        "child", cascade="all, delete-orphan"
    )


class ChildCreate(ChildBase):
    pass


class ChildPublic(ChildBase):
    id: int
    has_image: bool
