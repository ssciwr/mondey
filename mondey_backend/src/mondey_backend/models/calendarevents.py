from __future__ import annotations

import datetime

from sqlmodel import Field
from sqlmodel import SQLModel


class CalendarEventBase(SQLModel):
    title: str = ""
    description: str = ""
    external_link: str = ""
    event_date: datetime.datetime


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
    event_date: datetime.datetime | None = None
