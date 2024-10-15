from __future__ import annotations

from fastapi import APIRouter

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get("/auth/")
    def auth(current_active_researcher: CurrentActiveResearchDep):
        print(current_active_researcher.id)
        return {"ok": True}

    return router
