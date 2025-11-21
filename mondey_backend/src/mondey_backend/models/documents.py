from __future__ import annotations

import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class DocumentBase(SQLModel):
    title: str = ""
    description: str = ""
    filename: str = ""


class Document(DocumentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    uploaded_by_user_id: int


class DocumentCreate(DocumentBase):
    pass


class DocumentPublic(DocumentBase):
    id: int
    created_at: datetime.datetime
    uploaded_by_user_id: int


class DocumentAdmin(DocumentPublic):
    pass
