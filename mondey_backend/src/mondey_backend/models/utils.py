from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import attribute_keyed_dict
from sqlalchemy.orm import relationship
from sqlmodel import Field
from sqlmodel import Relationship


class ItemOrder(BaseModel):
    id: int
    order: int


class DeleteResponse(BaseModel):
    ok: bool
    dry_run: bool
    children: dict[str, int]
    error: str | None = Field(default=None, description="Error message when present")


def back_populates(name: str, **kwargs):
    # Workaround for "please state the generic argument using an annotation" sqlalchemy error
    # https://github.com/fastapi/sqlmodel/discussions/771#discussioncomment-10326074
    return Relationship(sa_relationship=relationship(back_populates=name, **kwargs))


def list_relationship(name: str, **kwargs):
    return Relationship(
        sa_relationship=relationship(
            back_populates=name,
            cascade="all, delete-orphan",
            **kwargs,
        )
    )


def dict_relationship(key: str):
    return Relationship(
        sa_relationship=relationship(
            collection_class=attribute_keyed_dict(key),
            cascade="all, delete-orphan",
        )
    )


def fixed_length_string_field(max_length: int, **kwargs):
    # bug in sqlmodel - max_length doesn't propagate to actual sqlalchemy column, so we explicitly set sa_type
    # https://github.com/fastapi/sqlmodel/discussions/746
    return Field(max_length=max_length, sa_type=String(max_length), **kwargs)  # type: ignore
