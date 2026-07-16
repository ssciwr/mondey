from __future__ import annotations

import dataclasses
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
from scipy.optimize import least_squares
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
from ..models.milestones import MilestoneAgeScoreCollection
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


def write_pdf_file(file: UploadFile, filename: pathlib.Path | str):
    max_file_size = 10 * 1024 * 1024  # 10MB
    try:
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)
        content = file.file.read()
        if len(content) > max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        with open(filename, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
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


def get_previously_achieved_milestone_ids(
    session: SessionDep, child_id: int | None, before: datetime.datetime
) -> set[int]:
    """
    The milestones that this child had already achieved before the given time, i.e. that
    they answered 3 for in an earlier completed answer session.

    Once a child answers 3 for a milestone it is no longer included in their later answer
    sessions (see `get_or_create_current_milestone_answer_session`), so it is absent from
    them. Such a milestone must be scored as 3 rather than having a value imputed for it:
    we know the child achieved it, and imputing the mean answer of children of their age
    would understate it, the more so the earlier they achieved it.

    :param session: the database session
    :param child_id: the child to look up
    :param before: only consider answer sessions created before this time
    :return: the ids of the milestones already achieved
    """
    milestone_ids = session.exec(
        select(col(MilestoneAnswer.milestone_id))
        .join(
            MilestoneAnswerSession,
            col(MilestoneAnswer.answer_session_id) == col(MilestoneAnswerSession.id),
        )
        .where(col(MilestoneAnswerSession.child_id) == child_id)
        .where(col(MilestoneAnswerSession.completed))
        .where(col(MilestoneAnswerSession.created_at) < before)
        .where(col(MilestoneAnswer.answer) == 3)
    ).all()
    return {milestone_id for milestone_id in milestone_ids if milestone_id is not None}


def iter_sessions_with_previously_achieved_milestone_ids(
    session: SessionDep,
    answer_sessions: Sequence[MilestoneAnswerSession],
) -> Iterable[tuple[MilestoneAnswerSession, set[int]]]:
    """Yield sessions chronologically with milestones achieved before each one.

    Achievement events for all completed sessions belonging to the relevant children
    are read in one ordered stream. This includes sessions excluded from statistics,
    because an answer of 3 in one of those sessions still explains why the milestone is
    absent from a later questionnaire.

    The yielded set is reused as iteration advances and must be consumed immediately.
    Sessions sharing a timestamp see the same prior state, matching the strict
    ``created_at < before`` behavior of :func:`get_previously_achieved_milestone_ids`.
    """
    ordered_sessions = sorted(
        answer_sessions,
        key=lambda answer_session: (
            answer_session.child_id,
            answer_session.created_at,
            answer_session.id or 0,
        ),
    )
    if not ordered_sessions:
        return

    child_ids = {answer_session.child_id for answer_session in ordered_sessions}
    achievement_query = (
        select(
            col(MilestoneAnswerSession.child_id),
            col(MilestoneAnswerSession.created_at),
            col(MilestoneAnswer.milestone_id),
        )
        .join(
            MilestoneAnswer,
            col(MilestoneAnswerSession.id) == col(MilestoneAnswer.answer_session_id),
        )
        .where(col(MilestoneAnswerSession.child_id).in_(child_ids))
        .where(col(MilestoneAnswerSession.completed))
        .where(col(MilestoneAnswer.answer) == 3)
        .order_by(
            col(MilestoneAnswerSession.child_id),
            col(MilestoneAnswerSession.created_at),
            col(MilestoneAnswerSession.id),
        )
        .execution_options(yield_per=1000)
    )
    achievement_events = iter(session.exec(achievement_query))
    next_event = next(achievement_events, None)
    current_child_id: int | None = None
    achieved_milestone_ids: set[int] = set()

    for answer_session in ordered_sessions:
        child_id = answer_session.child_id
        if child_id != current_child_id:
            current_child_id = child_id
            achieved_milestone_ids.clear()
            while next_event is not None and next_event[0] < child_id:
                next_event = next(achievement_events, None)

        while (
            next_event is not None
            and next_event[0] == child_id
            and next_event[1] < answer_session.created_at
        ):
            milestone_id = next_event[2]
            if milestone_id is not None:
                achieved_milestone_ids.add(milestone_id)
            next_event = next(achievement_events, None)

        yield answer_session, achieved_milestone_ids


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


def _get_expected_age_from_scores_heuristic(counts: np.ndarray) -> int:
    """
    The expected age for a milestone, as it was determined before the age curve was
    fitted: the youngest age at which the milestone is considered achieved. Only used by
    `get_milestone_ages_from_curve` as a fallback when no curve can be fitted, since a
    single child at a young age is enough to set the result.
    """
    achieved = np.array([_milestone_achieved(count) for count in counts])
    if not np.any(achieved):
        return app_settings.MAX_CHILD_AGE_MONTHS
    return int(np.argmax(achieved))


def _get_relevant_age_min_max_heuristic(
    expected_age: int, counts: np.ndarray
) -> tuple[int, int]:
    """
    The relevant age range for a milestone, as it was determined before the age curve was
    fitted. Only used by `get_milestone_ages_from_curve` as a fallback when no curve can
    be fitted.
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


# The mean answer at which a milestone is considered achieved. The answers are on a
# 0-3 scale, so 2.4 is 80% of the maximum, matching `_milestone_achieved` above.
MEAN_ANSWER_ACHIEVED = 2.4
# The mean answers delimiting the age range over which a milestone is worth asking:
# from when a few children can do it until nearly all of them can.
MEAN_ANSWER_RELEVANT_MIN = 0.3
MEAN_ANSWER_RELEVANT_MAX = 2.7
# The mean answer halfway between not achieved and achieved. The data has to contain
# answers from below and above this for the transition to be located at all.
MEAN_ANSWER_MIDPOINT = 1.5
# Bounds on the fitted steepness. A milestone whose fitted steepness sits on either
# bound has a transition that the data cannot resolve, so the fit is rejected.
MIN_STEEPNESS = 0.01
MAX_STEEPNESS = 2.0


def _mean_answer_to_logit(mean_answer: float) -> float:
    """Inverse of the logistic, mapping a mean answer in (0, 3) to a logit."""
    return float(np.log(mean_answer / (3.0 - mean_answer)))


@dataclasses.dataclass
class MilestoneAgeCurve:
    """
    A logistic fit of the mean answer for a milestone as a function of child age:

        mean_answer(age) = 3 / (1 + exp(-steepness * (age - midpoint)))

    The curve is parametrised by `expected_age` rather than by `midpoint`, so that
    the quantity we report and store is itself a fitted parameter. `expected_age` is
    the age at which the curve crosses `MEAN_ANSWER_ACHIEVED`, i.e. the age at which
    the milestone is typically achieved.

    `fit_ok` is False if there were too few answers, or if the fit did not converge
    to an identifiable transition, in which case the parameters must not be used.
    """

    expected_age: float
    steepness: float
    n_answers: int
    fit_ok: bool

    @classmethod
    def from_midpoint(
        cls, midpoint: float, steepness: float, n_answers: int
    ) -> MilestoneAgeCurve:
        """Reconstruct a curve from the midpoint and steepness that define it."""
        return cls(
            expected_age=midpoint
            + _mean_answer_to_logit(MEAN_ANSWER_ACHIEVED) / steepness,
            steepness=steepness,
            n_answers=n_answers,
            fit_ok=True,
        )

    @property
    def midpoint(self) -> float:
        """The age at which the mean answer is halfway between 0 and 3."""
        return self.expected_age - _mean_answer_to_logit(MEAN_ANSWER_ACHIEVED) / (
            self.steepness
        )

    def mean_answer(self, age: float | np.ndarray) -> float | np.ndarray:
        """The fitted mean answer for a child of this age in months."""
        return 3.0 / (1.0 + np.exp(-self.steepness * (age - self.midpoint)))

    def age_at_mean_answer(self, mean_answer: float) -> float:
        """The age in months at which the fitted curve reaches this mean answer."""
        return self.midpoint + _mean_answer_to_logit(mean_answer) / self.steepness


def fit_milestone_age_curve(counts: np.ndarray) -> MilestoneAgeCurve:
    """
    Fit a logistic curve of mean answer vs child age to the answers for a milestone.

    This is the single source of truth for a milestone's age curve: the expected age,
    the relevant age range, and the value imputed for a missing answer are all derived
    from it, so that they cannot drift apart.

    The fit is weighted by the number of answers at each age, so that ages with only a
    handful of answers cannot drag the curve, and uses a robust loss so that a noisy
    age does not dominate. Ages with no answers simply carry no weight, which is what
    lets the curve interpolate and extrapolate over gaps in the data.

    :param counts: the number of answers for each age and answer, where the index in the 2-d array is (age, answer)
    :return: the fitted MilestoneAgeCurve
    """
    ages = np.arange(counts.shape[0], dtype=float)
    n_per_age = counts.sum(axis=1)
    n_answers = int(n_per_age.sum())
    has_data = n_per_age > 0

    curve_failed = MilestoneAgeCurve(
        expected_age=float(app_settings.MAX_CHILD_AGE_MONTHS),
        steepness=MIN_STEEPNESS,
        n_answers=n_answers,
        fit_ok=False,
    )

    if n_answers < app_settings.MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT:
        return curve_failed
    # we need answers at more than one age to resolve a transition at all
    if np.count_nonzero(has_data) < 2:
        return curve_failed

    age = ages[has_data]
    n = n_per_age[has_data].astype(float)
    mean_answer = (counts[has_data] @ np.arange(4)) / n

    # The data has to bracket the transition for the curve to be identifiable: if every
    # child who was asked had already achieved the milestone (or none of them had), then
    # any number of curves fit the data equally well and the fitted parameters would be
    # arbitrary.
    if (
        mean_answer.min() > MEAN_ANSWER_MIDPOINT
        or mean_answer.max() < MEAN_ANSWER_MIDPOINT
    ):
        return curve_failed

    max_age = float(app_settings.MAX_CHILD_AGE_MONTHS)

    def residuals(params: np.ndarray) -> np.ndarray:
        expected_age, steepness = params
        midpoint = (
            expected_age - _mean_answer_to_logit(MEAN_ANSWER_ACHIEVED) / steepness
        )
        predicted = 3.0 / (1.0 + np.exp(-steepness * (age - midpoint)))
        # weight by sqrt(n) so each residual counts once per answer
        return np.sqrt(n) * (predicted - mean_answer)

    # initial guess: the youngest age whose mean answer is at or above the achieved
    # threshold, which is roughly what the old heuristic returned
    achieved_ages = age[mean_answer >= MEAN_ANSWER_ACHIEVED]
    expected_age_guess = (
        float(achieved_ages[0]) if achieved_ages.size else max_age / 2.0
    )
    try:
        fit = least_squares(
            residuals,
            x0=[np.clip(expected_age_guess, 0.0, max_age), 0.3],
            bounds=([0.0, MIN_STEEPNESS], [max_age, MAX_STEEPNESS]),
            loss="soft_l1",
            f_scale=0.5,
        )
    except (ValueError, RuntimeError) as e:
        logger.warning(f"Milestone age curve fit failed: {e}")
        return curve_failed

    if not fit.success:
        return curve_failed

    expected_age, steepness = float(fit.x[0]), float(fit.x[1])
    # A parameter on one of its bounds means the data does not resolve the transition.
    # In particular, an expected age on the upper bound means the answers cross the
    # midpoint but do not reach the achieved threshold within the supported age range.
    # Either way the fitted parameters are not meaningful, so reject the fit and fall
    # back to the heuristic.
    expected_age_on_bound = np.isclose(expected_age, 0.0) or np.isclose(
        expected_age, max_age
    )
    steepness_on_bound = (
        steepness <= MIN_STEEPNESS * 1.01 or steepness >= MAX_STEEPNESS * 0.99
    )
    if expected_age_on_bound or steepness_on_bound:
        return curve_failed

    return MilestoneAgeCurve(
        expected_age=expected_age,
        steepness=steepness,
        n_answers=n_answers,
        fit_ok=True,
    )


def milestone_age_curve_from_collection(
    collection: MilestoneAgeScoreCollection | None,
) -> MilestoneAgeCurve | None:
    """
    Reconstructs the fitted age curve for a milestone from its stored statistics.

    :param collection: the stored statistics for a milestone
    :return: the fitted age curve, or None if there is no usable curve for this milestone
    """
    if collection is None or not collection.curve_fit_ok:
        return None
    # reconstruct from the stored midpoint rather than from the stored expected_age,
    # which is rounded to whole months for display
    return MilestoneAgeCurve.from_midpoint(
        midpoint=collection.curve_midpoint,
        steepness=collection.curve_steepness,
        n_answers=collection.curve_n_answers,
    )


def get_milestone_curves(session: SessionDep) -> dict[int, MilestoneAgeCurve | None]:
    """
    The stored age curve for each milestone, as fitted by the last statistics update.

    :param session: the database session
    :return: milestone id -> its age curve, or None if it has no usable curve
    """
    return {
        collection.milestone_id: milestone_age_curve_from_collection(collection)
        for collection in session.exec(select(MilestoneAgeScoreCollection)).all()
    }


def get_milestone_ages_from_curve(
    curve: MilestoneAgeCurve, counts: np.ndarray
) -> tuple[int, int, int]:
    """
    Returns the expected age and the relevant age range for a milestone from its fitted
    age curve, falling back to the previous heuristics if the curve could not be fitted.

    :param curve: the fitted age curve for this milestone
    :param counts: the number of answers for each age and answer, where the index in the 2-d array is (age, answer)
    :return: expected age, min relevant age, max relevant age, in months
    """
    max_age = app_settings.MAX_CHILD_AGE_MONTHS
    if not curve.fit_ok:
        expected_age = _get_expected_age_from_scores_heuristic(counts)
        relevant_age_min, relevant_age_max = _get_relevant_age_min_max_heuristic(
            expected_age, counts
        )
        return expected_age, relevant_age_min, relevant_age_max

    def clamped_age(mean_answer: float) -> int:
        age = curve.age_at_mean_answer(mean_answer)
        return int(np.clip(round(age), 0, max_age))

    return (
        clamped_age(MEAN_ANSWER_ACHIEVED),
        clamped_age(MEAN_ANSWER_RELEVANT_MIN),
        clamped_age(MEAN_ANSWER_RELEVANT_MAX),
    )


def child_image_path(child_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.PRIVATE_FILES_PATH}/children/{child_id}.webp")


def milestone_image_path(milestone_image_id: int | None) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/m/{milestone_image_id}.webp")


def milestone_group_image_path(milestone_group_id: int) -> pathlib.Path:
    return pathlib.Path(
        f"{app_settings.STATIC_FILES_PATH}/mg/{milestone_group_id}.webp"
    )


def document_path(document_id: int) -> pathlib.Path:
    return pathlib.Path(f"{app_settings.STATIC_FILES_PATH}/documents/{document_id}.pdf")


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
