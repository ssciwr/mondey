from __future__ import annotations

from fastapi import APIRouter
from fastapi import Response

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep
from ..dependencies import SessionDep
from ..dependencies import UserAsyncSessionDep
from ..statistics import extract_research_data


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get("/data/")
    async def get_research_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        current_active_researcher: CurrentActiveResearchDep,
    ):
        if current_active_researcher.full_data_access:
            research_group_id_filter = None
        else:
            research_group_id_filter = current_active_researcher.research_group_id
        df = await extract_research_data(
            session, user_session, research_group_id_filter
        )
        return Response(df.to_json(orient="records"), media_type="application/json")

    return router
