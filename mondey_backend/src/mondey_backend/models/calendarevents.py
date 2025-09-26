from __future__ import annotations

import datetime

from pydantic import field_serializer
from pydantic import field_validator
from sqlmodel import Field
from sqlmodel import SQLModel


class CalendarEventBase(SQLModel):
    title: str = ""
    description: str = ""
    external_link: str = ""
    event_date: datetime.date

    @field_validator("event_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%d.%m.%Y").date()
        return v


class CalendarEvent(CalendarEventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventRead(CalendarEventBase):
    id: int

    @field_serializer("event_date")
    def serialize_event_date(self, value: datetime.date) -> str:
        return value.strftime("%d.%m.%Y")


class CalendarEventUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    external_link: str | None = None
    event_date: datetime.date | None = None

    @field_validator("event_date", mode="before")
    @classmethod  # maybe this can be extracted out to avoid duplication
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.datetime.strptime(v, "%d.%m.%Y").date()
        return v
