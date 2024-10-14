from __future__ import annotations

from fastapi import APIRouter

from ..dependencies import ResearchDep


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get("/auth/")
    def auth():
        return {"ok": True}

    return router
