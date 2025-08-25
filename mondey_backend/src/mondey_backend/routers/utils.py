from __future__ import annotations

import datetime
import pathlib
from collections.abc import Iterable
from collections.abc import Sequence
from typing import TypeVar

import numpy as np
import webp
from fastapi import HTTPException
from fastapi import UploadFile
from PIL import Image
from PIL import ImageOps
from sqlalchemy import func
from sqlmodel import SQLModel
from sqlmodel import col
from sqlmodel import select
from webp import WebPPreset

from ..dependencies import SessionDep
from ..logging import logger
from ..models.children import Child
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneText
from ..models.milestones import SuspiciousState
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


def write_image_file(file: UploadFile, filename: pathlib.Path | str):
    image_max_width = 1024
    image_max_height = 1024
    image_quality = 90
    try:
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with Image.open(file.file) as img:
            # remove EXIF Orientation tag if present
            ImageOps.exif_transpose(img, in_place=True)
            # ensure image is not too large
            if img.width > image_max_width or img.height > image_max_height:
                img = ImageOps.contain(img, (image_max_width, image_max_height))
            # save image in webp format: https://developers.google.com/speed/webp/docs/cwebp#options
            webp.save_image(
                img, filename, preset=WebPPreset.PHOTO, quality=image_quality
            )
    except Exception as e:
        logger.exception(e)
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
            db_text.sqlmodel_update(text.model_dump())
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


def ensure_texts_exist_for_language(session: SessionDep, lang_id: str):
    for milestone_group_id in session.exec(select(col(MilestoneGroup.id))).all():
        if not session.get(MilestoneGroupText, (milestone_group_id, lang_id)):
            session.add(
                MilestoneGroupText(group_id=milestone_group_id, lang_id=lang_id)
            )
    for milestone_id in session.exec(select(col(Milestone.id))).all():
        if not session.get(MilestoneText, (milestone_id, lang_id)):
            session.add(MilestoneText(milestone_id=milestone_id, lang_id=lang_id))
    for child_question_id in session.exec(select(col(ChildQuestion.id))).all():
        if not session.get(ChildQuestionText, (child_question_id, lang_id)):
            session.add(
                ChildQuestionText(child_question_id=child_question_id, lang_id=lang_id)
            )
    for user_question_id in session.exec(select(col(UserQuestion.id))).all():
        if not session.get(UserQuestionText, (user_question_id, lang_id)):
            session.add(
                UserQuestionText(user_question_id=user_question_id, lang_id=lang_id)
            )
    session.commit()


def delete_texts_for_language(session: SessionDep, lang_id: str):
    text_types: list[type[Text]] = [
        MilestoneGroupText,
        MilestoneText,
        ChildQuestionText,
        UserQuestionText,
    ]
    for text_type in text_types:
        for milestone_group_text in session.exec(
            select(text_type).where(col(text_type.lang_id) == lang_id)
        ).all():
            session.delete(milestone_group_text)
    session.commit()
    i18n_language_path(lang_id).unlink(missing_ok=True)


def session_remaining_seconds(
    milestone_answer_session: MilestoneAnswerSession,
) -> float:
    session_lifetime_days = 14
    return (
        milestone_answer_session.created_at
        + datetime.timedelta(days=session_lifetime_days)
        - datetime.datetime.now()
    ).total_seconds()


def _session_has_expired(milestone_answer_session: MilestoneAnswerSession) -> bool:
    return session_remaining_seconds(milestone_answer_session) <= 0


def current_milestone_answer_session(
    session: SessionDep, current_active_user: User, child: Child
) -> MilestoneAnswerSession | None:
    milestone_answer_session = session.exec(
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.user_id) == current_active_user.id)
        .where(col(MilestoneAnswerSession.child_id) == child.id)
        .where(~col(MilestoneAnswerSession.expired))
        .where(~col(MilestoneAnswerSession.completed))
        .order_by(col(MilestoneAnswerSession.created_at).desc())
    ).first()
    return milestone_answer_session


def latest_completed_milestone_answer_session(
    session: SessionDep, current_active_user: User, child: Child
) -> MilestoneAnswerSession | None:
    milestone_answer_session = session.exec(
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.user_id) == current_active_user.id)
        .where(col(MilestoneAnswerSession.child_id) == child.id)
        .where(col(MilestoneAnswerSession.completed))
        .order_by(col(MilestoneAnswerSession.created_at).desc())
    ).first()
    return milestone_answer_session


def get_or_create_current_milestone_answer_session(
    session: SessionDep, current_active_user: User, child: Child
) -> MilestoneAnswerSession:
    milestone_answer_session = current_milestone_answer_session(
        session, current_active_user, child
    )
    if milestone_answer_session and (
        _session_has_expired(milestone_answer_session)
        or milestone_answer_session.completed
    ):
        milestone_answer_session.expired = True
        session.add(milestone_answer_session)
        session.commit()
        session.refresh(milestone_answer_session)
    if milestone_answer_session is None or milestone_answer_session.expired:
        milestone_answer_session = MilestoneAnswerSession(
            child_id=child.id,
            user_id=current_active_user.id,
            created_at=datetime.datetime.now(),
            completed=False,
            expired=False,
            included_in_statistics=False,
            suspicious_state=SuspiciousState.unknown,
        )
        add(session, milestone_answer_session)
        child_age_months = get_child_age_in_months(child)
        # get all age-relevant milestones for this child
        milestones = session.exec(
            select(Milestone)
            .where(child_age_months >= col(Milestone.relevant_age_min))
            .where(child_age_months <= col(Milestone.relevant_age_max))
        ).all()
        prev_answer_session = latest_completed_milestone_answer_session(
            session, current_active_user, child
        )
        all_prev_answer_session_ids = session.exec(
            select(MilestoneAnswerSession.id)
            .where(col(MilestoneAnswerSession.child_id) == child.id)
            .where(col(MilestoneAnswerSession.completed))
        ).all()
        for milestone in milestones:
            # only include milestones if they have not already been achieved by this child
            if (
                prev_answer_session is None
                or session.exec(
                    select(MilestoneAnswer)
                    .where(col(MilestoneAnswer.milestone_id) == milestone.id)
                    .where(
                        col(MilestoneAnswer.answer_session_id).in_(
                            all_prev_answer_session_ids
                        )
                    )
                    .where(col(MilestoneAnswer.answer) == 3)
                ).first()
                is None
            ):
                session.add(
                    MilestoneAnswer(
                        answer_session_id=milestone_answer_session.id,
                        milestone_id=milestone.id,
                        milestone_group_id=milestone.group_id,
                        answer=-1,
                    )
                )
        # also include any unachieved milestones from the previous session
        if prev_answer_session is not None:
            relevant_milestone_ids = {m.id for m in milestones}
            for (
                prev_milestone_id,
                milestone_answer,
            ) in prev_answer_session.answers.items():
                if (
                    milestone_answer.answer < 3
                    and prev_milestone_id not in relevant_milestone_ids
                ):
                    prev_milestone = session.get(Milestone, prev_milestone_id)
                    if prev_milestone is not None:
                        session.add(
                            MilestoneAnswer(
                                answer_session_id=milestone_answer_session.id,
                                milestone_id=prev_milestone_id,
                                milestone_group_id=prev_milestone.group_id,
                                answer=-1,
                            )
                        )
        session.commit()
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


def get_answer_session_child_age_in_months(
    session: SessionDep, answer_session: MilestoneAnswerSession
) -> int:
    child = session.get(Child, answer_session.child_id)
    if child is None:
        raise ValueError("No Child with id: ", answer_session.child_id)
    return get_child_age_in_months(child, answer_session.created_at)


def get_answer_session_child_ages_in_months(
    session: SessionDep, answer_sessions: Sequence[MilestoneAnswerSession]
) -> dict[int, int]:
    return {
        answer_session.id: get_answer_session_child_age_in_months(
            session, answer_session
        )
        for answer_session in answer_sessions
        if answer_session.id is not None
    }


def _milestone_achieved(answers: np.ndarray) -> bool:
    """
    Check if a milestone is considered achieved based on the answers.
    Milestone is considered achieved if:
      - at least 80% of the answers are 2 or 3
      - and at least 3 answers are provided.
    """
    # require at least `min_number_of_answers`
    min_number_of_answers = 3
    # required fraction of children that answered with 2 or 3 to consider the milestone achieved
    min_fraction_achieved = 0.8
    n = np.sum(answers)
    sufficient_data = n >= min_number_of_answers
    milestone_achieved = np.sum(answers[2:]) >= min_fraction_achieved * n
    return sufficient_data and milestone_achieved


def get_expected_age_from_scores(counts: np.ndarray) -> int:
    """
    Returns the expected age for a milestone based on the counts of each answer for each child age.
    :param counts: the number of answers for each age and answer, where the index in the 2-d array is (age, answer)
    :return: the expected age in months for this milestone
    """
    achieved = np.array([_milestone_achieved(count) for count in counts])
    if not np.any(achieved):
        return app_settings.MAX_CHILD_AGE_MONTHS
    return int(np.argmax(achieved))


def get_relevant_age_min_max(expected_age: int, counts: np.ndarray) -> tuple[int, int]:
    """
    Returns the min and max child age for which this milestone should be asked, based on the counts of each answer for each child age.
    :param expected_age: the expected age in months for this milestone
    :param counts: the number of answers for each age and answer, where the index in the 2-d array is (age, answer)
    :return: min, max relevant child age in months for this milestone
    """
    # require at least `min_number_of_answers`
    min_number_of_answers = 3
    # set max_age to only exclude ages with no 0 or 1 answers
    max_age = app_settings.MAX_CHILD_AGE_MONTHS
    while (
        np.sum(counts[max_age][:2]) == 0
        and np.sum(counts[max_age]) >= min_number_of_answers
        and max_age >= expected_age
    ):
        max_age -= 1
    min_age = 0
    # set min_age to only exclude ages with no 3 or 4 answers
    while (
        np.sum(counts[min_age][2:]) == 0
        and np.sum(counts[min_age]) >= min_number_of_answers
        and min_age <= expected_age
    ):
        min_age += 1
    return min_age, max_age


def child_image_path(child_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.PRIVATE_FILES_PATH}/children/{child_id}.webp")


def milestone_image_path(milestone_image_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/m/{milestone_image_id}.webp")


def milestone_group_image_path(milestone_group_id: int) -> pathlib.Path:
    return pathlib.Path(
        f"{app_settings.STATIC_FILES_PATH}/mg/{milestone_group_id}.webp"
    )


def submitted_milestone_image_path(
    submitted_milestone_image_id: int | None,
) -> pathlib.Path:
    return pathlib.Path(
        f"{app_settings.STATIC_FILES_PATH}/ms/{submitted_milestone_image_id}.webp"
    )


def i18n_language_path(language_id: str) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/i18n/{language_id}.json")


def get_milestonegroups_for_answersession(
    session: SessionDep, answersession: MilestoneAnswerSession
) -> dict[int, MilestoneGroup]:
    check_for_overlap = (
        select(Milestone.group_id)
        .where(col(Milestone.id).in_(answersession.answers.keys()))
        .distinct()
    )
    return {
        m.id: m  # type: ignore
        for m in session.exec(
            select(MilestoneGroup).where(col(MilestoneGroup.id).in_(check_for_overlap))
        ).all()
    }


def count_milestone_answers_for_milestone(
    session: SessionDep, milestone_id: int
) -> int:
    count_query = (
        select(func.count())
        .select_from(MilestoneAnswer)
        .where(MilestoneAnswer.milestone_id == milestone_id)
    )
    return session.exec(count_query).one()


def get_childs_answering_sessions(
    session: SessionDep, child_id: int
) -> list[MilestoneAnswerSession]:
    select_answering_sessions = select(MilestoneAnswerSession).where(
        col(MilestoneAnswerSession.child_id) == child_id
    )
    return list(session.exec(select_answering_sessions).all())
