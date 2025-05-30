from __future__ import annotations

from sqlmodel import Field
from sqlmodel import SQLModel


class ChildBase(SQLModel):
    name: str = ""
    birth_year: int
    birth_month: int
    color: str | None = None


class Child(ChildBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    has_image: bool


class ChildCreate(ChildBase):
    pass


class ChildPublic(ChildBase):
    id: int
    has_image: bool


class ChildSummaryPublic(ChildPublic):
    active_answer_session: bool
    session_progress: float
    session_remaining_seconds: float
