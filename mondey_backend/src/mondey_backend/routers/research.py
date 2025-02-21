from __future__ import annotations

from fastapi import APIRouter

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep
from ..dependencies import SessionDep
from ..dependencies import UserAsyncSessionDep
from ..statistics import extract_research_data


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get("/data/", response_model=list[dict[str, str | int | float]])
    async def get_research_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        current_active_researcher: CurrentActiveResearchDep,
    ):
        if current_active_researcher.full_data_access:
            research_group_id_filter = None
        else:
            research_group_id_filter = current_active_researcher.research_group_id
        return await extract_research_data(
            session, user_session, research_group_id_filter
        )

    return router
