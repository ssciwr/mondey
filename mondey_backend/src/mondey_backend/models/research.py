from __future__ import annotations

from sqlmodel import Field
from sqlmodel import SQLModel


class ResearchGroup(SQLModel, table=True):
    id: int = Field(primary_key=True)
