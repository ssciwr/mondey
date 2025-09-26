from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.calendarevents import CalendarEvent
from ..models.calendarevents import CalendarEventRead


def create_router() -> APIRouter:
    router = APIRouter(prefix="/events", tags=["events"])

    @router.get("/", response_model=list[CalendarEventRead])
    def get_events(session: SessionDep):
        events = session.exec(
            select(CalendarEvent).order_by(col(CalendarEvent.event_date).desc())
        ).all()
        return events

    return router
