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

    return router
