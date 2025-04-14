from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.questions import ChildQuestion
from ..models.questions import ChildQuestionPublic
from ..models.questions import UserQuestion
from ..models.questions import UserQuestionPublic


def create_router() -> APIRouter:
    router = APIRouter(tags=["questions"])

    @router.get("/user-questions/", response_model=list[UserQuestionPublic])
    def get_user_questions(
        session: SessionDep,
    ):
        user_questions = session.exec(
            select(UserQuestion)
            .where(UserQuestion.visibility)
            .order_by(UserQuestion.order)
        ).all()

        return user_questions

    @router.get("/child-questions/", response_model=list[ChildQuestionPublic])
    def get_child_questions(session: SessionDep):
        child_questions = session.exec(
            select(ChildQuestion)
            .where(ChildQuestion.visibility)
            .order_by(ChildQuestion.order)
        ).all()
        return child_questions

    return router
