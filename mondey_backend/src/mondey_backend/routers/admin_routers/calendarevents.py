from __future__ import annotations

from fastapi import APIRouter

from ...dependencies import SessionDep
from ...models.calendarevents import CalendarEvent
from ...models.calendarevents import CalendarEventCreate
from ...models.calendarevents import CalendarEventRead
from ...models.calendarevents import CalendarEventUpdate
from ..utils import add
from ..utils import get


def create_router() -> APIRouter:
    router = APIRouter()

    @router.post("/calendarevents/", response_model=CalendarEventRead)
    def create_event(session: SessionDep, event: CalendarEventCreate):
        db_event = CalendarEvent.model_validate(event)
        add(session, db_event)
        session.refresh(db_event)
        return db_event

    @router.put("/calendarevents/{event_id}", response_model=CalendarEventRead)
    def update_event(
        session: SessionDep, event_id: int, event_update: CalendarEventUpdate
    ):
        db_event = get(session, CalendarEvent, event_id)
        db_event.sqlmodel_update(event_update.model_dump(exclude_unset=True))
        add(session, db_event)
        return db_event

    @router.delete("/calendarevents/{event_id}")
    def delete_event(session: SessionDep, event_id: int):
        db_event = get(session, CalendarEvent, event_id)
        session.delete(db_event)
        session.commit()
        return {"ok": True}

    return router
