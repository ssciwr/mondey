from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import col
from sqlmodel import select

from ...dependencies import SessionDep
from ...models.milestones import Language
from ...models.questions import ChildQuestion
from ...models.questions import ChildQuestionAdmin
from ...models.questions import ChildQuestionText
from ...models.questions import UserQuestion
from ...models.questions import UserQuestionAdmin
from ...models.questions import UserQuestionText
from ...models.utils import ItemOrder
from ..utils import add
from ..utils import get
from ..utils import update_child_question_text
from ..utils import update_item_orders
from ..utils import update_user_question_text


def create_router() -> APIRouter:
    router = APIRouter()

    # User question CRUD endpoints
    @router.get("/user-questions/", response_model=list[UserQuestionAdmin])
    def get_user_questions_admin(session: SessionDep):
        user_questions = session.exec(
            select(UserQuestion).order_by(col(UserQuestion.order))
        ).all()
        return user_questions

    @router.post("/user-questions/", response_model=UserQuestionAdmin)
    def create_user_question(session: SessionDep):
        user_question = UserQuestion()
        add(session, user_question)
        for language in session.exec(select(Language)).all():
            session.add(
                UserQuestionText(user_question_id=user_question.id, lang_id=language.id)
            )
        session.commit()
        session.refresh(user_question)
        return user_question

    @router.put("/user-questions/", response_model=UserQuestionAdmin)
    def update_user_question(
        session: SessionDep,
        user_question: UserQuestionAdmin,
    ):
        db_user_question = get(session, UserQuestion, user_question.id)
        for key, value in user_question.model_dump(exclude={"text"}).items():
            setattr(db_user_question, key, value)
        update_user_question_text(session, user_question)
        add(session, db_user_question)
        return db_user_question

    @router.delete("/user-questions/{user_question_id}")
    def delete_user_question(session: SessionDep, user_question_id: int):
        question = get(session, UserQuestion, user_question_id)
        session.delete(question)
        session.commit()
        return {"ok": True}

    @router.post("/user-questions/order/")
    def order_user_questions_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, UserQuestion, item_orders)
        return {"ok": True}

    # Child question CRUD endpoints
    @router.get("/child-questions/", response_model=list[ChildQuestionAdmin])
    def get_child_questions_admin(session: SessionDep):
        user_questions = session.exec(
            select(ChildQuestion).order_by(col(ChildQuestion.order))
        ).all()
        return user_questions

    @router.post("/child-questions/", response_model=ChildQuestionAdmin)
    def create_child_question(
        session: SessionDep,
    ):
        child_question = ChildQuestion()
        add(session, child_question)
        for language in session.exec(select(Language)).all():
            session.add(
                ChildQuestionText(
                    child_question_id=child_question.id, lang_id=language.id
                )
            )
        session.commit()
        session.refresh(child_question)
        return child_question

    @router.put("/child-questions/", response_model=ChildQuestionAdmin)
    def update_child_question(
        session: SessionDep,
        child_question: ChildQuestionAdmin,
    ):
        db_child_question = get(session, ChildQuestion, child_question.id)

        for key, value in child_question.model_dump(exclude={"text"}).items():
            setattr(db_child_question, key, value)
        update_child_question_text(session, child_question)
        add(session, db_child_question)
        return db_child_question

    @router.delete("/child-questions/{child_question_id}")
    def delete_child_question(session: SessionDep, child_question_id: int):
        question = get(session, ChildQuestion, child_question_id)
        session.delete(question)
        session.commit()
        return {"ok": True}

    @router.post("/child-questions/order/")
    def order_child_questions_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, ChildQuestion, item_orders)
        return {"ok": True}

    return router
