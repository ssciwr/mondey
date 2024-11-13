from __future__ import annotations

import datetime
import logging
import pathlib
from collections.abc import Iterable
from collections.abc import Sequence
from typing import TypeVar

import numpy as np
from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import SQLModel
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.children import Child
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScores
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneText
from ..models.questions import ChildQuestionAdmin
from ..models.questions import ChildQuestionText
from ..models.questions import UserQuestionAdmin
from ..models.questions import UserQuestionText
from ..users import User

Text = MilestoneText | MilestoneGroupText | UserQuestionText | ChildQuestionText


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


Entity = TypeVar("Entity")


def get(session: SessionDep, entity: type[Entity], ident: int | str) -> Entity:
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


def update_child_question_text(session: SessionDep, child_question: ChildQuestionAdmin):
    _update_text(
        session, ChildQuestionText, child_question.text.values(), child_question.id
    )


def _session_has_expired(milestone_answer_session: MilestoneAnswerSession) -> bool:
    session_lifetime_days = 7
    return (
        datetime.datetime.now() - milestone_answer_session.created_at
        > datetime.timedelta(days=session_lifetime_days)
    )


def get_or_create_current_milestone_answer_session(
    session: SessionDep, current_active_user: User, child_id: int
) -> MilestoneAnswerSession:
    get_db_child(session, current_active_user, child_id)
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
            user_id=current_active_user.id,
            created_at=datetime.datetime.now(),
        )
        add(session, milestone_answer_session)
    return milestone_answer_session


def get_child_age_in_months(child: Child, date: datetime.date | None = None) -> int:
    if date is None:
        date = datetime.date.today()
    return (date.year - child.birth_year) * 12 + (date.month - child.birth_month)


def get_db_child(
    session: SessionDep, current_active_user: User, child_id: int
) -> Child:
    child = get(session, Child, child_id)
    if child is None or child.user_id != current_active_user.id:
        raise HTTPException(
            404, detail=f"Child with id {child_id} not found or wrong user"
        )
    return child


def _get_answer_session_child_ages_in_months(session: SessionDep) -> dict[int, int]:
    answer_sessions = session.exec(select(MilestoneAnswerSession)).all()
    return {
        answer_session.id: get_child_age_in_months(  # type: ignore
            get(session, Child, answer_session.child_id), answer_session.created_at
        )
        for answer_session in answer_sessions
    }


def _get_expected_age_from_scores(scores: np.ndarray) -> int:
    # placeholder algorithm: returns first age with avg score > 3
    return np.argmax(scores >= 3.0)


def _get_average_scores_by_age(
    answers: Sequence[MilestoneAnswer], child_ages: dict[int, int]
) -> np.ndarray:
    max_age_months = 72
    scores = np.zeros(max_age_months + 1)
    counts = np.zeros_like(scores)
    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        # convert 0-3 answer index to 1-4 score
        scores[age] += answer.answer + 1
        counts[age] += 1
    # divide each score by the number of answers
    with np.errstate(invalid="ignore"):
        scores /= counts
    # replace NaNs (due to zero counts) with zeros
    scores = np.nan_to_num(scores)
    return scores


def calculate_milestone_age_scores(
    session: SessionDep, milestone_id: int
) -> MilestoneAgeScores:
    child_ages = _get_answer_session_child_ages_in_months(session)
    answers = session.exec(
        select(MilestoneAnswer).where(col(MilestoneAnswer.milestone_id) == milestone_id)
    ).all()
    scores = _get_average_scores_by_age(answers, child_ages)
    expected_age = _get_expected_age_from_scores(scores)
    return MilestoneAgeScores(
        expected_age=expected_age,
        scores=[
            MilestoneAgeScore(
                age_months=age,
                avg_score=score,
                expected_score=(4 if age >= expected_age else 1),
            )
            for age, score in enumerate(scores)
        ],
    )
