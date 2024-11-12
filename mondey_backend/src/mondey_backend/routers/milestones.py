from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy.orm import lazyload
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAnswer
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
        session: SessionDep, current_active_user: CurrentActiveUserDep, 
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
        answer_session  = (
            get_or_create_current_milestone_answer_session(
                session, current_active_user, child_id
            )
        )
        all_answers = session.exec(
            select(MilestoneAnswer).where(
                MilestoneAnswer.answer_session_id == answer_session.id
            )
        ).all()

        # FIXME: this needs to be done better, as it contains a cumbersome 
        # type conversion that should be avoided. 
        # when fixing: -make sure pydantic is still as much in effect as possible 
        # - check if we need it at all. certainly a nice thing
        milestone_groups_public = []
        for mgroup in milestone_groups: 
            p = 0.0
            mgroup_public = MilestoneGroupPublic(
                id=mgroup.id,
                order=mgroup.order,
                text=mgroup.text,
                milestones=mgroup.milestones
            )
            for milestone in mgroup.milestones: 
                answer = next((answer for answer in all_answers if answer.milestone_id == milestone.id), None)

                logging.getLogger("mondey-frontend-prototype-backend-1").info(answer)
                logging.getLogger("mondey-frontend-prototype-backend-1").info(
                    [
                        answer
                        for answer in all_answers
                        if answer.milestone_id == milestone.id
                    ]
                )

                if answer is not None and answer != "":
                    p += 1.0 

            mgroup_public.progress = p / len(mgroup.milestones)  
            milestone_groups_public.append(mgroup_public)

        return milestone_groups_public

    return router
