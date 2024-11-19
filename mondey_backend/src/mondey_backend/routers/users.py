from __future__ import annotations

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
from ..models.questions import ChildAnswer
from ..models.questions import ChildAnswerPublic
from ..models.questions import UserAnswer
from ..models.questions import UserAnswerPublic
from ..models.users import UserRead
from ..models.users import UserUpdate
from ..users import fastapi_users
from .scores import TrafficLight
from .scores import compute_feedback_for_milestonegroup
from .utils import _session_has_expired
from .utils import add
from .utils import child_image_path
from .utils import get
from .utils import get_child_age_in_months
from .utils import get_db_child
from .utils import get_or_create_current_milestone_answer_session
from .utils import write_file


def create_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

    # children endpoints
    @router.get("/children/", response_model=list[ChildPublic])
    def get_children(session: SessionDep, current_active_user: CurrentActiveUserDep):
        children = session.exec(
            select(Child).where(col(Child.user_id) == current_active_user.id)
        ).all()
        return children

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
        for key, value in child.model_dump().items():
            setattr(db_child, key, value)
        session.commit()
        return db_child

    @router.delete("/children/{child_id}")
    def delete_child(
        session: SessionDep, current_active_user: CurrentActiveUserDep, child_id: int
    ):
        child = get_db_child(session, current_active_user, child_id)
        session.delete(child)
        session.commit()
        return {"ok": True}

    @router.get("/children-images/{child_id}", response_class=FileResponse)
    async def get_child_image(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
    ):
        child = get_db_child(session, current_active_user, child_id)
        image_path = child_image_path(child_id)
        if child.has_image and image_path.exists():
            return image_path
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
        write_file(file, child_image_path(child_id))
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
        milestone_answer_session = get(
            session, MilestoneAnswerSession, milestone_answer_session_id
        )
        if milestone_answer_session.user_id != current_active_user.id:
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
                for key, value in new_answer.model_dump().items():
                    setattr(current_answer, key, value)

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
                for key, value in new_answer.model_dump().items():
                    setattr(current_answer, key, value)
        session.commit()

        return {"ok": True}

    @router.get(
        "/feedback/child={child_id}/milestonegroup={milestonegroup_id}",
        response_model=dict[str, tuple[int, dict[int, int]] | int],
    )
    def get_feedback_for_milestonegroup(
        session: SessionDep,
        current_active_user: CurrentActiveUserDep,
        child_id: int,
        milestonegroup_id: int,
        with_detailed: bool = False,
    ) -> dict[str, tuple[int, dict[int, int]] | int]:
        results: dict[str, tuple[int, dict[int, int]] | int] = {}
        # get all answer sessions and filter for completed ones
        answersessions = [
            a
            for a in session.exec(
                select(MilestoneAnswerSession).where(
                    col(MilestoneAnswerSession.child_id) == child_id
                    and col(MilestoneAnswerSession.user_id) == current_active_user.id
                )
            ).all()
            if _session_has_expired(a)
        ]
        if answersessions == []:
            return {"unknown": TrafficLight.invalid.value}  # type: ignore
        else:
            for answersession in answersessions:
                child = get_db_child(
                    session, current_active_user, answersession.child_id
                )
                result = compute_feedback_for_milestonegroup(
                    session,
                    milestonegroup_id,
                    answersession,
                    get_child_age_in_months(child, answersession.created_at),
                    age_limit_low=6,
                    age_limit_high=6,
                    with_detailed=with_detailed,
                )
            datestring = answersession.created_at.strftime("%Y-%m-%d")
            if with_detailed:
                total, detailed = result  # type: ignore
                results[datestring] = (total, detailed)
            else:
                results[datestring] = result  # type: ignore
        return results

    return router
