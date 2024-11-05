from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.orm import lazyload
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.children import Child
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupPublic
from ..models.milestones import MilestonePublic
from .utils import get
from .utils import get_child_age_in_months


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
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        delta_months = 6
        child = get(session, Child, child_id)
        if child.user_id != current_active_user.id:
            raise HTTPException(401)
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
        return milestone_groups

    return router
