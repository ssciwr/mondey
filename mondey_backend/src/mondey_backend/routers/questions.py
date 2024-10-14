from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.questions import UserQuestion
from ..models.questions import UserQuestionPublic


def create_router() -> APIRouter:
    router = APIRouter(tags=["questions"])

    @router.get("/user-questions/", response_model=list[UserQuestionPublic])
    def get_user_questions(
        session: SessionDep,
    ):
        user_questions = session.exec(
            select(UserQuestion).order_by(col(UserQuestion.order))
        ).all()
        return user_questions

    return router
