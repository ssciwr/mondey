from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy.orm import lazyload
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupPublic
from ..models.milestones import MilestonePublic
from .utils import get
from .utils import get_child_age_in_months
from .utils import get_db_child
from .utils import get_or_create_current_milestone_answer_session


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
        delta_months = 6
        child = get_db_child(session, current_active_user, child_id)

        child_age_months = get_child_age_in_months(child)
        milestone_groups = session.exec(
            select(MilestoneGroup)
            .order_by(col(MilestoneGroup.order))
            .options(
                lazyload(
                    MilestoneGroup.milestones.and_(
                        (
                            child_age_months
                            >= col(Milestone.expected_age_months) - delta_months
                        )
                        & (
                            child_age_months
                            <= col(Milestone.expected_age_months) + delta_months
                        )
                    )
                )
            )
        ).all()

        # compute progress from milestone answers. While this is not
        # the most efficient way, it is the least intrusive and concentrates
        # progress reporting in the least amount of code - this function and the
        # MilestonAnswerPublic model.
        # The actual database does not need to know about progress - it's
        # a derived value only for being displayed to the user.

        answer_session = get_or_create_current_milestone_answer_session(
            session, current_active_user, child_id
        )

        milestone_groups_public = []
        for mgroup in milestone_groups:
            mgroup_public = MilestoneGroupPublic(
                id=mgroup.id,
                order=mgroup.order,
                text=mgroup.text,
                milestones=mgroup.milestones,
            )
            mgroup_public.progress = 0.0

            if len(mgroup.milestones) > 0:
                for milestone in mgroup.milestones:
                    if milestone.id is None:
                        continue

                    answer = answer_session.answers.get(milestone.id)

                    if answer is not None and answer.answer >= 0:
                        mgroup_public.progress += 1.0

                mgroup_public.progress /= len(mgroup.milestones)

            milestone_groups_public.append(mgroup_public)

        return milestone_groups_public

    return router
