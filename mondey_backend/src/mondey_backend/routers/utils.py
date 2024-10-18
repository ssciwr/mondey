from __future__ import annotations

import datetime
import logging
import pathlib
from collections.abc import Iterable

from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import SQLModel
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.children import Child
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneAgeGroup
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneText
from ..models.questions import UserQuestionAdmin
from ..models.questions import UserQuestionText
from ..users import User

Text = MilestoneText | MilestoneGroupText | UserQuestionText


def write_file(file: UploadFile, filename: str):
    logging.warning(f"Saving file {file.filename} to {filename}")
    try:
        pathlib.Path(filename).parent.mkdir(exist_ok=True)
        contents = file.file.read()
        with open(filename, "wb") as f:
            f.write(contents)
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=404, detail="Error saving uploaded file") from e
    finally:
        file.file.close()


def get(session: SessionDep, entity: type, ident: int):
    instance = session.get(entity, ident)
    if not instance:
        raise HTTPException(
            status_code=404, detail=f"{entity} with id {ident} not found"
        )
    return instance


def add(session: SessionDep, instance: SQLModel):
    session.add(instance)
    session.commit()
    session.refresh(instance)


def _update_text(
    session: SessionDep, entity: type[Text], texts: Iterable[Text], ident: int
):
    for text in texts:
        db_text = session.get(entity, (ident, text.lang_id))
        if not db_text:
            db_text = text
        else:
            for key, value in text.model_dump().items():
                setattr(db_text, key, value)
        session.add(db_text)


def update_milestone_text(session: SessionDep, milestone: MilestoneAdmin):
    _update_text(session, MilestoneText, milestone.text.values(), milestone.id)


def update_milestone_group_text(
    session: SessionDep, milestone_group: MilestoneGroupAdmin
):
    _update_text(
        session, MilestoneGroupText, milestone_group.text.values(), milestone_group.id
    )


def update_user_question_text(session: SessionDep, user_question: UserQuestionAdmin):
    _update_text(
        session, UserQuestionText, user_question.text.values(), user_question.id
    )


def _session_has_expired(milestone_answer_session: MilestoneAnswerSession) -> bool:
    session_lifetime_days = 7
    return (
        datetime.datetime.now() - milestone_answer_session.created_at
        > datetime.timedelta(days=session_lifetime_days)
    )


def get_child_age_in_months(child: Child) -> int:
    today = datetime.date.today()
    return (today.year - child.birth_year) * 12 + (today.month - child.birth_month)


def get_milestone_age_group_id(session: SessionDep, child: Child) -> int:
    child_age_in_months = get_child_age_in_months(child)
    milestone_age_group = session.exec(
        select(MilestoneAgeGroup).where(
            (col(MilestoneAgeGroup.months_min) <= child_age_in_months)
            & (child_age_in_months < col(MilestoneAgeGroup.months_max))
        )
    ).one_or_none()
    if milestone_age_group is None or milestone_age_group.id is None:
        raise HTTPException(404, "No milestone age group found for this child")
    return milestone_age_group.id


def get_or_create_current_milestone_answer_session(
    session: SessionDep, current_active_user: User, child_id: int
):
    child = session.get(Child, child_id)
    if child is None or child.user_id != current_active_user.id:
        raise HTTPException(401)
    milestone_age_group_id = get_milestone_age_group_id(session, child)
    milestone_answer_session = session.exec(
        select(MilestoneAnswerSession)
        .where(
            (col(MilestoneAnswerSession.user_id) == current_active_user.id)
            & (col(MilestoneAnswerSession.child_id) == child_id)
        )
        .order_by(col(MilestoneAnswerSession.created_at).desc())
    ).first()
    if milestone_answer_session is None or _session_has_expired(
        milestone_answer_session
    ):
        milestone_answer_session = MilestoneAnswerSession(
            child_id=child_id,
            age_group_id=milestone_age_group_id,
            user_id=current_active_user.id,
            created_at=datetime.datetime.now(),
        )
        add(session, milestone_answer_session)
    return milestone_answer_session
