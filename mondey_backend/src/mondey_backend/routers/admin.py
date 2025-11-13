from __future__ import annotations

from fastapi import APIRouter

from ..dependencies import AdminDep
from .admin_routers import calendarevents
from .admin_routers import documents
from .admin_routers import languages
from .admin_routers import milestones
from .admin_routers import questions
from .admin_routers import research
from .admin_routers import settings
from .admin_routers import users


def create_router() -> APIRouter:
    router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[AdminDep])
    router.include_router(calendarevents.create_router())
    router.include_router(documents.create_router())
    router.include_router(languages.create_router())
    router.include_router(milestones.create_router())
    router.include_router(questions.create_router())
    router.include_router(settings.create_router())
    router.include_router(users.create_router())
    router.include_router(research.create_router())
    return router
