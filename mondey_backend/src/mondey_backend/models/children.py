from __future__ import annotations

from sqlmodel import Field
from sqlmodel import SQLModel


class ChildBase(SQLModel):
    name: str = ""
    birth_year: int
    birth_month: int
    has_image: bool


class Child(ChildBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int


class ChildCreate(ChildBase):
    pass


class ChildPublic(ChildBase):
    id: int
