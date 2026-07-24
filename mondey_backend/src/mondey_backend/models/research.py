from __future__ import annotations

from pydantic import BaseModel
from sqlmodel import Field
from sqlmodel import SQLModel


class ResearchGroup(SQLModel, table=True):
    id: int = Field(primary_key=True)


class ImportCsvResponse(BaseModel):
    message: str
    children_imported: int
