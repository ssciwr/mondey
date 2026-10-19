from __future__ import annotations

from pydantic import NaiveDatetime
from sqlmodel import Field
from sqlmodel import SQLModel


class CalendarEventBase(SQLModel):
    title: str = ""
    description: str = ""
    external_link: str = ""
    # The calendar UI supplies a date, not an instant in time. Keep its local
    # midnight representation so timezone conversion cannot change the day.
    event_date: NaiveDatetime


class CalendarEvent(CalendarEventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventRead(CalendarEventBase):
    id: int


class CalendarEventUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    external_link: str | None = None
    event_date: NaiveDatetime | None = None
