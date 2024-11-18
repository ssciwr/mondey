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
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScores
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupAgeScore
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneText
from ..models.questions import ChildQuestion
from ..models.questions import ChildQuestionAdmin
from ..models.questions import ChildQuestionText
from ..models.questions import UserQuestion
from ..models.questions import UserQuestionAdmin
from ..models.questions import UserQuestionText
from ..models.utils import ItemOrder
from ..settings import app_settings
from ..users import User

Text = MilestoneText | MilestoneGroupText | UserQuestionText | ChildQuestionText
OrderedItem = Milestone | MilestoneGroup | UserQuestion | ChildQuestion


def write_file(file: UploadFile, filename: pathlib.Path | str):
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


def update_item_orders(
    session: SessionDep, entity: type[OrderedItem], item_orders: Iterable[ItemOrder]
):
    for item_order in item_orders:
        db_item = get(session, entity, item_order.id)
        db_item.order = item_order.order
    session.commit()


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
    if child.user_id != current_active_user.id and not current_active_user.is_superuser:
        raise HTTPException(
            404, detail=f"User does not have access to Child with id {child_id}"
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
) -> tuple[np.ndarray, np.ndarray]:
    max_age_months = 72
    avg_scores = np.zeros(max_age_months + 1)
    sigma_scores = np.zeros(max_age_months + 1)
    counts = np.zeros_like(avg_scores)

    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        # convert 0-3 answer index to 1-4 score
        avg_scores[age] += answer.answer + 1
        counts[age] += 1

    # divide each score by the number of answers
    with np.errstate(invalid="ignore"):
        avg_scores /= counts

    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        sigma_scores[age] += (answer.answer + 1 - avg_scores[age]) ** 2

    with np.errstate(invalid="ignore"):
        sigma_scores = np.sqrt(sigma_scores / np.max(counts - 1, 0))

    # replace NaNs (due to zero counts) with zeros
    avg = np.nan_to_num(avg_scores)
    sigma = np.nan_to_num(sigma_scores)

    return avg, sigma


def calculate_milestone_age_scores(
    session: SessionDep, milestone_id: int
) -> MilestoneAgeScores:
    child_ages = _get_answer_session_child_ages_in_months(session)
    answers = session.exec(
        select(MilestoneAnswer).where(col(MilestoneAnswer.milestone_id) == milestone_id)
    ).all()
    avg, sigma = _get_average_scores_by_age(answers, child_ages)
    expected_age = _get_expected_age_from_scores(avg)
    return MilestoneAgeScores(
        expected_age=expected_age,
        scores=[
            MilestoneAgeScore(
                milestone_id=milestone_id,
                age_months=age,
                avg_score=avg[age],
                sigma_score=sigma[age],
                expected_score=(4 if age >= expected_age else 1),
            )
            for age in range(0, len(avg))
        ],
    )


def calculate_milestone_group_age_scores(
    session: SessionDep,
    milestone_group_id: int,
    age: int,
    age_lower: int,
    age_upper: int,
) -> MilestoneGroupAgeScore:
    milestonegroup = get(session, MilestoneGroup, milestone_group_id)

    all_answers = []
    for milestone in milestonegroup.milestones:
        answers = [
            answer.answer
            for answer in session.exec(
                select(MilestoneAnswer).where(
                    col(MilestoneAnswer.milestone_id) == milestone.id
                    and age_lower <= milestone.expected_age_months <= age_upper
                )
            ).all()
        ]
        all_answers.extend(answers)

    avg_group = np.nan_to_num(np.mean(all_answers))
    sigma_group = np.nan_to_num(np.std(all_answers))
    mg_score = MilestoneGroupAgeScore(
        age_months=age,
        group_id=milestonegroup.id,
        avg_score=avg_group,
        sigma_score=sigma_group,
    )
    return mg_score


def child_image_path(child_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.PRIVATE_FILES_PATH}/children/{child_id}.jpg")


def milestone_image_path(milestone_image_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/m/{milestone_image_id}.jpg")


def milestone_group_image_path(milestone_group_id: int) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/mg/{milestone_group_id}.jpg")


def i18n_language_path(language_id: str) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/i18n/{language_id}.json")
