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
    """
    Compute average and standard deviation of scores for each age class that
    is observed in the answers.

    Parameters
    ----------
    answers : Sequence[MilestoneAnswer]
        list of answer objects
    child_ages : dict[int, int]
        dictionary mapping child answer session ids to ages in months

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        tuple of the form (a, s) where a, are numpy arrays containing the average and standard deviation of the scores for each age in months.
    """

    max_age_months = 72
    avg_scores = np.zeros(max_age_months + 1)
    stddev_scores = np.zeros(max_age_months + 1)
    counts = np.zeros_like(avg_scores)
    if child_ages == {}:
        return avg_scores, stddev_scores

    # compute average
    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        # convert 0-3 answer index to 1-4 score
        avg_scores[age] += answer.answer + 1
        counts[age] += 1

    with np.errstate(invalid="ignore"):
        avg_scores /= counts

    # compute standard deviation
    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        stddev_scores[age] += (answer.answer + 1 - avg_scores[age]) ** 2

    with np.errstate(invalid="ignore"):
        stddev_scores = np.sqrt(stddev_scores / np.max(counts - 1, 0))

    # replace NaNs (due to zero counts) with zeros
    avg = np.nan_to_num(avg_scores)
    stddev = np.nan_to_num(stddev_scores)

    return avg, stddev


def calculate_milestone_age_scores(
    session: SessionDep,
    milestone_id: int,
) -> MilestoneAgeScores:
    """
    Calculate the average and standard deviation of the scores for a milestone
    at each age in months. This uses all available answers for a milestone.
    Parameters
    ----------
    session : SessionDep
        database session
    milestone_id : int
        id of the milestone to compute the statistics for
    Returns
    -------
    MilestoneAgeScores
        MilestoneAgeScores object containing the average and standard deviation of the scores for a single milestone for each age in range of ages the mondey system looks at.
    """
    child_ages = _get_answer_session_child_ages_in_months(session)

    answers = session.exec(
        select(MilestoneAnswer).where(col(MilestoneAnswer.milestone_id) == milestone_id)
    ).all()
    avg, stddev = _get_average_scores_by_age(answers, child_ages)
    expected_age = _get_expected_age_from_scores(avg)

    return MilestoneAgeScores(
        expected_age=expected_age,
        scores=[
            MilestoneAgeScore(
                milestone_id=milestone_id,
                age_months=age,
                avg_score=avg[age],
                stddev_score=stddev[age],
                expected_score=(4 if age >= expected_age else 1),
            )
            for age in range(0, len(avg))
        ],
    )


def calculate_milestone_group_age_scores(
    session: SessionDep,
    milestonegroup: MilestoneGroup,
    age: int,
    age_lower: int = 6,
    age_upper: int = 6,
) -> MilestoneGroupAgeScore:
    """
    Calculate the average and standard deviation of the scores for a milestone group at a given age range. The age range is defined by the age parameter and the age_lower and age_upper parameters: [age - age_lower, age + age_upper]. This uses all available answers for a milestone group.

    Parameters
    ----------
    session : SessionDep
        database session
    milestonegroup : MilestoneGroup
        Milestonegroup to calculate the scores for
    age : int
        age in months to use as the anchor for the age range
    age_lower : int, optional
        value to compute the lower bound for the age range, by default 6
    age_upper : int, optional
        value to compute the upper bound for the age range, by default 6

    Returns
    -------
    MilestoneGroupAgeScore
        Struct containing the average and standard deviation of the scores for a single milestone group
    """
    answers = []
    for milestone in milestonegroup.milestones:
        m_answers = [
            answer.answer
            for answer in session.exec(
                select(MilestoneAnswer).where(
                    col(MilestoneAnswer.milestone_id) == milestone.id
                    and age_lower <= milestone.expected_age_months <= age_upper
                )
            ).all()
        ]
        answers.extend(m_answers)

    answers = np.array(answers) + 1  # convert 0-3 answer index to 1-4 score
    avg_group = np.nan_to_num(np.mean(answers))
    stddev_group = np.nan_to_num(np.std(answers, correction=1))
    mg_score = MilestoneGroupAgeScore(
        age_months=age,
        group_id=milestonegroup.id,
        avg_score=avg_group,
        stddev_score=stddev_group,
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
