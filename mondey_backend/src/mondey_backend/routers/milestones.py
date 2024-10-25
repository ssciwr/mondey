from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupPublic
from ..models.milestones import MilestonePublic
from .utils import get


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

    @router.get("/milestone-groups/", response_model=list[MilestoneGroupPublic])
    def get_milestone_groups(session: SessionDep):
        milestone_groups = session.exec(
            select(MilestoneGroup).order_by(col(MilestoneGroup.order))
        ).all()
        return milestone_groups

    @router.get(
        "/milestone-groups/{milestone_group_id}", response_model=MilestoneGroupPublic
    )
    def get_milestone_group(session: SessionDep, milestone_group_id: int):
        return get(session, MilestoneGroup, milestone_group_id)

    return router
