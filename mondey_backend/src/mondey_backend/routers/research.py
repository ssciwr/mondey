from __future__ import annotations

import json

import pandas as pd
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlmodel import select
from starlette.concurrency import run_in_threadpool

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep
from ..dependencies import SessionDep
from ..dependencies import UserAsyncSessionDep
from ..logging import logger
from ..models.milestones import Milestone
from ..models.questions import ChildQuestion
from ..models.questions import UserQuestion
from ..statistics import iter_research_data


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get(
        "/data/",
        response_class=StreamingResponse,
        responses={200: {"content": {"application/jsonl": {}}}},
    )
    async def get_research_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        current_active_researcher: CurrentActiveResearchDep,
    ):
        """Return research records as a stream of JSON Lines.

        A progress record naming each stage precedes one data record containing
        the array of records. Errors after streaming starts produce an error
        record instead.
        """
        if current_active_researcher.full_data_access:
            research_group_id_filter = None
        else:
            research_group_id_filter = current_active_researcher.research_group_id

        def progress(stage: str) -> str:
            return json.dumps({"type": "progress", "stage": stage}) + "\n"

        def to_json_bytes(df: pd.DataFrame) -> bytes:
            return df.to_json(orient="records").encode()

        async def events():
            try:
                async for update in iter_research_data(
                    session, user_session, research_group_id_filter
                ):
                    if isinstance(update, str):
                        yield progress(update)
                    else:
                        yield progress("transferring")
                        data = await run_in_threadpool(to_json_bytes, update)
                        # Sent whole so it is compressed as a single block.
                        yield b'{"type":"data","data":'
                        yield data
                        yield b"}\n"
            except Exception:
                logger.exception("Research data extraction failed")
                # HTTP headers have already been sent; report failure in-band.
                yield '{"type":"error"}\n'

        return StreamingResponse(
            events(),
            media_type="application/jsonl",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

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
