from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import col
from sqlmodel import delete
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.children import Child
from ..models.children import ChildCreate
from ..models.children import ChildPublic
from ..models.children import ChildSummaryPublic
from ..models.milestones import MilestoneAnswerPublic
from ..models.milestones import MilestoneAnswerResponse
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneAnswerSessionPublic
from ..models.milestones import MilestoneGroupPublic
from ..models.questions import ChildAnswer
from ..models.questions import ChildAnswerPublic
from ..models.questions import UserAnswer
from ..models.questions import UserAnswerPublic
from ..models.users import UserRead
from ..models.users import UserUpdate
from ..models.utils import DeleteResponse
from ..users import fastapi_users
from .scores import compute_milestonegroup_feedback_detailed
from .scores import compute_milestonegroup_feedback_summary
from .utils import add
from .utils import child_image_path
from .utils import current_milestone_answer_session
from .utils import get
from .utils import get_childs_answering_sessions
from .utils import get_db_child
from .utils import get_milestonegroups_for_answersession
from .utils import get_or_create_current_milestone_answer_session
from .utils import session_remaining_seconds
from .utils import write_image_file


def create_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

    # children endpoints
    @router.get("/children/", response_model=list[ChildSummaryPublic])
    def get_children(session: SessionDep, current_active_user: CurrentActiveUserDep):
        child_summaries: list[ChildSummaryPublic] = []
        children = session.exec(
            select(Child).where(col(Child.user_id) == current_active_user.id)
        ).all()
        for child in children:
            milestone_answer_session = current_milestone_answer_session(
                session, current_active_user, child
            )
            child_summary = ChildSummaryPublic.model_validate(
                child,
                update={
                    "active_answer_session": False,
                    "session_progress": 0,
                    "session_remaining_seconds": 0,
                },
            )
            if milestone_answer_session is not None:
                child_summary.active_answer_session = True
                answers = np.array(
                    list(a.answer for a in milestone_answer_session.answers.values())
                )
                child_summary.session_progress = np.mean(answers >= 0, dtype=np.float64)
                child_summary.session_remaining_seconds = session_remaining_seconds(
                    milestone_answer_session
                )
            child_summaries.append(child_summary)
        return child_summaries

    @router.get("/children/{child_id}", response_model=ChildPublic)
    def get_child(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        child = get_db_child(session, current_active_user, child_id)
        return child

    @router.post("/children/", response_model=ChildPublic)
    def create_child(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child: ChildCreate,
    ):
        if datetime(child.birth_year, child.birth_month, 1) > datetime.now():
            raise HTTPException(400, "Birth date must be in the past")

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
        db_child = get_db_child(session, current_active_user, child.id)
        db_child.sqlmodel_update(child.model_dump())
        session.commit()
        return db_child

    @router.delete("/children/{child_id}", response_model=DeleteResponse)
    def delete_child(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
        dry_run: bool = Query(
            True,
            description="When true, shows what would be deleted without actually deleting",
        ),
    ):
        child = get_db_child(session, current_active_user, child_id)
        # the above guards it to only owners of the child.
        affected_child_answers = 0
        for answering_session in get_childs_answering_sessions(session, child_id):
            affected_child_answers += len(answering_session.answers)
        if dry_run:
            return {
                "ok": True,
                "dry_run": dry_run,
                "children": {"affectedAnswers": affected_child_answers},
            }

        child_image_path(child_id).unlink(missing_ok=True)

        delete_milestone_statement = delete(MilestoneAnswerSession).where(
            col(MilestoneAnswerSession.child_id) == child_id
        )
        session.execute(delete_milestone_statement)

        delete_answers_statement = delete(ChildAnswer).where(
            col(ChildAnswer.child_id) == child_id
        )

        session.execute(delete_answers_statement)
        session.delete(child)
        session.commit()

        return {
            "ok": True,
            "dry_run": dry_run,
            "children": {"affectedAnswers": affected_child_answers},
        }

    @router.get("/children-images/{child_id}", response_class=FileResponse)
    async def get_child_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
    ):
        child = get_db_child(session, current_active_user, child_id)
        image_path = child_image_path(child_id)
        if child.has_image and image_path.exists():
            return FileResponse(image_path, media_type="image/webp")
        raise HTTPException(404)

    @router.put("/children-images/{child_id}")
    async def upload_child_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
        file: UploadFile,
    ):
        child = get_db_child(session, current_active_user, child_id)
        child.has_image = True
        session.commit()
        write_image_file(file, child_image_path(child_id))
        return {"ok": True}

    @router.delete("/children-images/{child_id}")
    async def delete_child_image(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        child = get_db_child(session, current_active_user, child_id)
        child.has_image = False
        session.commit()
        child_image_path(child.id).unlink(missing_ok=True)
        return {"ok": True}

    # milestone endpoints
    @router.get(
        "/milestone-answers/{child_id}", response_model=MilestoneAnswerSessionPublic
    )
    def get_current_milestone_answer_session(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        child = get_db_child(session, current_active_user, child_id)
        milestone_answer_session = get_or_create_current_milestone_answer_session(
            session, current_active_user, child
        )
        return milestone_answer_session

    @router.put(
        "/milestone-answers/{milestone_answer_session_id}",
        response_model=MilestoneAnswerResponse,
    )
    def update_milestone_answer(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        milestone_answer_session_id: int,
        answer: MilestoneAnswerPublic,
    ):
        milestone_answer_session = get(
            session, MilestoneAnswerSession, milestone_answer_session_id
        )
        if milestone_answer_session.user_id != current_active_user.id:
            raise HTTPException(401)
        if milestone_answer_session.expired:
            raise HTTPException(401, "Answer session has expired")
        milestone_answer = milestone_answer_session.answers.get(answer.milestone_id)
        if milestone_answer is None:
            raise HTTPException(401)
        milestone_answer.answer = answer.answer
        session.commit()
        session.refresh(milestone_answer_session)
        logging.warning(milestone_answer_session)
        if all(a.answer >= 0 for a in milestone_answer_session.answers.values()):
            logging.warning(
                sum(a.answer >= 0 for a in milestone_answer_session.answers.values())
            )
            milestone_answer_session.expired = True
            milestone_answer_session.completed = True
            session.add(milestone_answer_session)
            session.commit()
            session.refresh(milestone_answer_session)
        return MilestoneAnswerResponse(
            answer=MilestoneAnswerPublic.model_validate(milestone_answer),
            session_completed=milestone_answer_session.completed,
        )

    # Endpoints for answers to user question
    @router.get("/user-answers/", response_model=list[UserAnswerPublic])
    def get_current_user_answers(
        session: SessionDep, current_active_user: CurrentActiveUserDep
    ):
        answers = session.exec(
            select(UserAnswer).where(col(UserAnswer.user_id) == current_active_user.id)
        ).all()

        return answers

    @router.put("/user-answers/", response_model=list[UserAnswerPublic])
    def update_current_user_answers(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        new_answers: list[UserAnswerPublic],
    ):
        for new_answer in new_answers:
            current_answer = session.get(
                UserAnswer, (current_active_user.id, new_answer.question_id)
            )

            if current_answer is None:
                current_answer = UserAnswer.model_validate(
                    new_answer, update={"user_id": current_active_user.id}
                )
                add(session, current_answer)
            else:
                current_answer.sqlmodel_update(new_answer.model_dump())

        session.commit()
        return new_answers

    # Endpoints for answers to child question
    @router.get(
        "/children-answers/{child_id}", response_model=dict[int, ChildAnswerPublic]
    )
    def get_current_child_answers(
        session: SessionDep, child_id: int, current_active_user: CurrentActiveUserDep
    ):
        get_db_child(session, current_active_user, child_id)
        answers = session.exec(
            select(ChildAnswer).where(col(ChildAnswer.child_id) == child_id)
        ).all()

        return {answer.question_id: answer for answer in answers}

    @router.put("/children-answers/{child_id}")
    def update_current_child_answers(
        session: SessionDep,
        child_id: int,
        current_active_user: CurrentActiveUserDep,
        new_answers: dict[int, ChildAnswerPublic],
    ):
        get_db_child(session, current_active_user, child_id)

        for new_answer in new_answers.values():
            current_answer = session.get(
                ChildAnswer, (child_id, new_answer.question_id)
            )

            if current_answer is None:
                current_answer = ChildAnswer.model_validate(
                    new_answer,
                    update={
                        "child_id": child_id,
                    },
                )
                session.add(current_answer)
            else:
                current_answer.sqlmodel_update(new_answer.model_dump())
        session.commit()

        return {"ok": True}

    @router.get(
        "/milestone-answers-sessions/{child_id}",
        response_model=dict[int, MilestoneAnswerSessionPublic],
    )
    def get_completed_milestone_answer_sessions(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ) -> dict[int, MilestoneAnswerSessionPublic]:
        milestone_answer_sessions = {
            mas.id: mas  # type: ignore
            for mas in session.exec(
                select(MilestoneAnswerSession).where(
                    (col(MilestoneAnswerSession.user_id) == current_active_user.id)
                    & (col(MilestoneAnswerSession.child_id) == child_id)
                    & col(MilestoneAnswerSession.completed)
                )
            ).all()
        }
        return milestone_answer_sessions  # type: ignore

    @router.get(
        "/feedback/answersession={answersession_id}",
        response_model=dict[int, MilestoneGroupPublic],
    )
    def get_milestonegroups_for_session(
        session: SessionDep,
        answersession_id: int,
    ):
        answersession = get(session, MilestoneAnswerSession, answersession_id)
        return get_milestonegroups_for_answersession(session, answersession)

    @router.get(
        "/feedback/answersession={answersession_id}/summary",
        response_model=dict[int, int],
    )
    def get_summary_feedback_for_answersession(
        session: SessionDep,
        answersession_id: int,
    ) -> dict[int, int]:
        answersession = get(session, MilestoneAnswerSession, answersession_id)
        feedback = compute_milestonegroup_feedback_summary(session, answersession)
        return feedback

    @router.get(
        "/feedback/answersession={answersession_id}/detailed",
        response_model=dict[int, dict[int, int]],
    )
    def get_detailed_feedback_for_answersession(
        session: SessionDep,
        answersession_id: int,
    ) -> dict[int, dict[int, int]]:
        answersession = get(session, MilestoneAnswerSession, answersession_id)
        feedback = compute_milestonegroup_feedback_detailed(session, answersession)
        return feedback

    return router
