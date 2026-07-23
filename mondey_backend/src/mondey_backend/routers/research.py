from __future__ import annotations

from fastapi import APIRouter
from fastapi import Response
from sqlmodel import select

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep
from ..dependencies import SessionDep
from ..dependencies import UserAsyncSessionDep
from ..models.milestones import Milestone
from ..models.questions import ChildQuestion
from ..models.questions import UserQuestion
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

    @router.get("/names/", response_model=dict[str, dict[int, str]])
    async def get_research_names(session: SessionDep, lang_id: str = "de"):
        milestones = session.exec(select(Milestone)).all()

        def milestone_label(milestone: Milestone) -> str:
            group_text = milestone.group.text.get(lang_id)
            milestone_text = milestone.text.get(lang_id)
            return " :: ".join(
                part
                for part in (
                    milestone.name,
                    group_text.title if group_text else "",
                    milestone_text.title if milestone_text else "",
                )
                if part
            )

        return {
            "milestone": {m.id: m.name for m in milestones},
            "milestone_label": {m.id: milestone_label(m) for m in milestones},
            "user_question": {
                q.id: q.name for q in session.exec(select(UserQuestion)).all()
            },
            "child_question": {
                q.id: q.name for q in session.exec(select(ChildQuestion)).all()
            },
        }

    return router
