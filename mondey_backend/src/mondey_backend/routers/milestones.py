from __future__ import annotations

from fastapi import APIRouter
from fastapi import UploadFile
from sqlalchemy.orm import lazyload
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.milestones import AgeInterval
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupPublic
from ..models.milestones import MilestonePublic
from ..models.milestones import SubmittedMilestoneImage
from .utils import add
from .utils import get
from .utils import get_db_child
from .utils import get_or_create_current_milestone_answer_session
from .utils import submitted_milestone_image_path
from .utils import write_image_file


def create_router() -> APIRouter:
    router = APIRouter(tags=["milestones"])

    @router.get("/languages/", response_model=list[str])
    def get_languages(
        session: SessionDep,
    ):
        return [language.id for language in session.exec(select(Language)).all()]

    @router.get("/milestones/", response_model=list[MilestonePublic])
    def get_milestones(
        session: SessionDep,
    ):
        milestones = session.exec(
            select(Milestone).order_by(col(Milestone.order))
        ).all()
        return milestones

    @router.get("/milestones/{milestone_id}", response_model=MilestonePublic)
    def get_milestone(session: SessionDep, milestone_id: int):
        return get(session, Milestone, milestone_id)

    @router.get(
        "/milestone-groups/{child_id}", response_model=list[MilestoneGroupPublic]
    )
    def get_milestone_groups(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
    ):
        child = get_db_child(session, current_active_user, child_id)
        milestone_answer_session = get_or_create_current_milestone_answer_session(
            session, current_active_user, child
        )
        milestone_ids = list(milestone_answer_session.answers.keys())
        print("milestone_ids", milestone_ids)
        milestone_groups = session.exec(
            select(MilestoneGroup)
            .order_by(col(MilestoneGroup.order))
            .options(
                lazyload(
                    MilestoneGroup.milestones.and_(col(Milestone.id).in_(milestone_ids))
                )
            )
        ).all()

        return milestone_groups

    @router.post("/submitted-milestone-images/{milestone_id}")
    async def submit_milestone_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        milestone_id: int,
        file: UploadFile,
    ):
        milestone = get(session, Milestone, milestone_id)
        submitted_milestone_image = SubmittedMilestoneImage(
            milestone_id=milestone.id, user_id=current_active_user.id
        )
        add(session, submitted_milestone_image)
        write_image_file(
            file, submitted_milestone_image_path(submitted_milestone_image.id)
        )
        return {"ok": True}

    @router.get("/age-intervals", response_model=list[AgeInterval])
    def get_age_intervals(session: SessionDep):
        return session.exec(select(AgeInterval)).all()

    @router.post("/age-intervals")
    def create_age_interval(session: SessionDep, lower_limit: int, upper_limit: int):
        age_interval = AgeInterval(lower_limit=lower_limit, upper_limit=upper_limit)
        add(session, age_interval)
        return {"ok", True}

    return router
