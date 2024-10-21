from __future__ import annotations

import pathlib

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.children import Child
from ..models.children import ChildCreate
from ..models.children import ChildPublic
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerPublic
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneAnswerSessionPublic
from ..models.questions import UserAnswer
from ..models.questions import UserAnswerPublic
from ..models.users import UserRead
from ..models.users import UserUpdate
from ..settings import app_settings
from ..users import fastapi_users
from .utils import add
from .utils import get
from .utils import get_or_create_current_milestone_answer_session
from .utils import write_file


def create_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

    # children endpoints
    @router.get("/children/", response_model=list[ChildPublic])
    def get_children(session: SessionDep, current_active_user: CurrentActiveUserDep):
        return [
            child
            for child in session.exec(
                select(Child).where(col(Child.user_id) == current_active_user.id)
            ).all()
        ]

    @router.post("/children/", response_model=ChildPublic)
    def create_child(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child: ChildCreate,
    ):
        db_child = Child.model_validate(
            child, update={"user_id": current_active_user.id, "has_image": False}
        )
        add(session, db_child)
        return db_child

    @router.put("/children/", response_model=ChildPublic)
    def update_child(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child: ChildPublic,
    ):
        db_child = get(session, Child, child.id)
        if db_child is None or db_child.user_id != current_active_user.id:
            raise HTTPException(401)
        for key, value in child.model_dump().items():
            setattr(db_child, key, value)
        add(session, db_child)
        return db_child

    @router.delete("/children/{child_id}")
    def delete_child(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        child = get(session, Child, child_id)
        if child.user_id != current_active_user.id:
            raise HTTPException(401)
        session.delete(child)
        session.commit()
        return {"ok": True}

    @router.get("/children-images/{child_id}", response_class=FileResponse)
    async def get_child_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
    ):
        child = get(session, Child, child_id)
        if child.user_id != current_active_user.id:
            raise HTTPException(401)
        image_path = pathlib.Path(
            f"{app_settings.PRIVATE_FILES_PATH}/children/{child.id}.jpg"
        )
        if not image_path.exists():
            raise HTTPException(404)
        return image_path

    @router.put("/children-images/{child_id}")
    async def upload_child_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
        file: UploadFile,
    ):
        child = get(session, Child, child_id)
        if child.user_id != current_active_user.id:
            raise HTTPException(401)
        child.has_image = True
        session.commit()
        filename = f"{app_settings.PRIVATE_FILES_PATH}/children/{child.id}.jpg"
        write_file(file, filename)
        return {"ok": True}

    # milestone endpoints
    @router.get(
        "/milestone-answers/{child_id}", response_model=MilestoneAnswerSessionPublic
    )
    def get_current_milestone_answer_session(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        milestone_answer_session = get_or_create_current_milestone_answer_session(
            session, current_active_user, child_id
        )
        return milestone_answer_session

    @router.put(
        "/milestone-answers/{milestone_answer_session_id}",
        response_model=MilestoneAnswerPublic,
    )
    def update_milestone_answer(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        milestone_answer_session_id: int,
        answer: MilestoneAnswerPublic,
    ):
        milestone_answer_session = session.get(
            MilestoneAnswerSession, milestone_answer_session_id
        )
        if (
            milestone_answer_session is None
            or milestone_answer_session.user_id != current_active_user.id
        ):
            raise HTTPException(401)
        milestone_answer = milestone_answer_session.answers.get(answer.milestone_id)
        if milestone_answer is None:
            milestone_answer = MilestoneAnswer(
                answer_session_id=milestone_answer_session.id,
                milestone_id=answer.milestone_id,
                answer=answer.answer,
            )
            add(session, milestone_answer)
        else:
            milestone_answer.answer = answer.answer
            session.commit()
        return milestone_answer

    # Endpoints for answers to user question
    @router.get("/user-answers/{user_id}", response_model=list[UserAnswerPublic])
    def get_current_user_answers(
        session: SessionDep, current_active_user: CurrentActiveUserDep
    ):
        # TODO: check if there is answer data for the current user in the database,
        # if not, create it and return the new empty struct
        # else return the found stuff

        try:
            print("userid: ", current_active_user.id)

            user_answers = [
                UserAnswerPublic(id=answer.id, answer=answer.answer)
                for answer in session.exec(
                    select(UserAnswer).where(
                        col(UserAnswer.user_id) == current_active_user.id
                    )
                ).all()
            ]

            print("normal operation: get_current_user_answers")
            return user_answers

        except Exception as err:
            print("shit happened when getting current answers")
            raise HTTPException(500) from err

    @router.post("/user-answers/{user_id}", response_model=list[UserAnswerPublic])
    def create_user_answers(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        user_answers: list[UserAnswerPublic],
    ):
        print("user_answer_session: ", session)
        if session is None:
            raise HTTPException(401)

        for answer in user_answers:
            full_answer = UserAnswer(
                id=answer.id, user_id=current_active_user.id, answer=answer.answer
            )
            db_useranswers = UserAnswer.model_validate(full_answer)
            add(session, db_useranswers)

        return user_answers

    @router.put("/user-answers/{user_id}", response_model=list[UserAnswerPublic])
    def update_current_user_answers(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        new_answers: list[UserAnswerPublic],
    ):
        print("user_answer_session: ", session)
        if session is None:
            raise HTTPException(401)

        answers_of_user = {
            answer.id: answer
            for answer in session.exec(
                select(UserAnswer).where(UserAnswer.user_id == current_active_user.id)
            ).all()
        }

        for new_answer in new_answers:
            if new_answer is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"UserAnswer with id {new_answer.id} not found",
                )
            else:
                stored_answer = answers_of_user[new_answer.id]

                print(
                    "normal operation: update_current_user_answers",
                    session,
                    new_answer.id,
                    new_answer.answer,
                    stored_answer.answer,
                )

                stored_answer.answer = new_answer.answer
                session.add(stored_answer)

        session.commit()

        return new_answers

    return router
