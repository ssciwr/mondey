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
from sqlmodel import delete
from sqlmodel import select
from webp import WebPPreset

from ..dependencies import SessionDep
from ..logging import logger
from ..models.children import Child
from ..models.milestones import AdminSettings
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneAgeCurveParams
from ..models.milestones import MilestoneAgeScoreCollection
from ..models.milestones import MilestoneAgeScoreCollectionPublic
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneText
from ..models.milestones import SuspiciousState
from ..models.questions import ChildAnswer
from ..models.questions import ChildQuestion
from ..models.questions import ChildQuestionAdmin
from ..models.questions import ChildQuestionText
from ..models.questions import UserAnswer
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
    sessions, but we need to score it as a 3 rather than imputing the value from the curve.
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
    """Yield sessions chronologically with milestones achieved before each one."""
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


def get_db_milestone_answer_session(
    session: SessionDep,
    current_active_user: User,
    answer_session_id: int,
) -> MilestoneAnswerSession:
    answer_session = get(session, MilestoneAnswerSession, answer_session_id)
    if (
        answer_session.user_id != current_active_user.id
        and not current_active_user.is_superuser
    ):
        raise HTTPException(
            404,
            detail=(
                "User does not have access to MilestoneAnswerSession "
                f"with id {answer_session_id}"
            ),
        )
    return answer_session


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


# The mean answer at the midpoint of the curve, halfway between 0 and 3. The data has to
# contain answers from below and above this for the transition to be located at all.
MEAN_ANSWER_MIDPOINT = 1.5
# Lower bound on the fitted steepness. A milestone whose fitted steepness sits on this
# bound has a flat curve, i.e. a transition that the data cannot resolve, so the fit is
# rejected.
MIN_STEEPNESS = 0.01
# Upper bound on the fitted steepness. Unlike the lower bound this is not a rejection
# criterion: a sharp transition is perfectly well determined, and the minimum relevant
# age margin (see `get_milestone_ages_from_curve`) is what keeps its age range usable.
# It is here only so that the fit terminates: ages are whole months, so above this the
# curve is already saturated at every age either side of the midpoint and the optimiser
# would otherwise keep increasing the steepness for no gain.
MAX_STEEPNESS = 50.0


def _mean_answer_to_logit(mean_answer: float) -> float:
    """Inverse of the logistic, mapping a mean answer in (0, 3) to a logit."""
    return float(np.log(mean_answer / (3.0 - mean_answer)))


# the largest argument to exp that does not overflow a float64
_MAX_EXP_ARG = 700.0


def _logistic_mean_answer(
    age: float | np.ndarray, midpoint: float, steepness: float
) -> float | np.ndarray:
    """
    The logistic mean answer curve, clipped so that an arbitrarily steep curve cannot
    overflow: beyond the clip the curve is already 0 or 3 to machine precision.
    """
    exponent = np.clip(-steepness * (age - midpoint), -_MAX_EXP_ARG, _MAX_EXP_ARG)
    return 3.0 / (1.0 + np.exp(exponent))


@dataclasses.dataclass
class MilestoneAgeCurve:
    """
    A logistic fit of the mean answer for a milestone as a function of child age:

        mean_answer(age) = 3 / (1 + exp(-steepness * (age - midpoint)))

    `midpoint` and `steepness` are the fitted parameters, and are what is stored: the
    ages we report are derived from the curve afterwards, at admin-configurable
    thresholds (see `get_milestone_ages_from_curve`), so that changing those thresholds
    re-derives the ages without refitting anything.

    `fit_ok` is False if there were too few answers, or if the fit did not converge
    to an identifiable transition, in which case the parameters must not be used.
    """

    midpoint: float
    steepness: float
    n_answers: int
    fit_ok: bool

    def mean_answer(self, age: float | np.ndarray) -> float | np.ndarray:
        """The fitted mean answer for a child of this age in months."""
        return _logistic_mean_answer(age, self.midpoint, self.steepness)

    def age_at_mean_answer(self, mean_answer: float) -> float:
        """The age in months at which the fitted curve reaches this mean answer."""
        return self.midpoint + _mean_answer_to_logit(mean_answer) / self.steepness


def fit_milestone_age_curve(counts: np.ndarray) -> MilestoneAgeCurve:
    """Fit a logistic curve of mean answer vs child age to the answers for a milestone."""
    ages = np.arange(counts.shape[0], dtype=float)
    n_per_age = counts.sum(axis=1)
    n_answers = int(n_per_age.sum())
    has_data = n_per_age > 0

    curve_failed = MilestoneAgeCurve(
        midpoint=0.0,
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
        midpoint, steepness = params
        # scale each residual by sqrt(n) so that an age with many answers counts for
        # more than one with few. The robust loss below means the cost of an age does
        # not grow with n as fast as this scaling suggests, which is the point: a
        # well-sampled but unrepresentative age still cannot dominate the fit.
        return np.sqrt(n) * (
            _logistic_mean_answer(age, midpoint, steepness) - mean_answer
        )

    # initial guess: the youngest age whose mean answer is at or above the midpoint,
    # which the check above guarantees exists
    midpoint_guess = float(age[mean_answer >= MEAN_ANSWER_MIDPOINT][0])
    try:
        fit = least_squares(
            residuals,
            x0=[np.clip(midpoint_guess, 0.0, max_age), 0.3],
            bounds=([0.0, MIN_STEEPNESS], [max_age, MAX_STEEPNESS]),
            loss="soft_l1",
            f_scale=0.5,
        )
    except (ValueError, RuntimeError) as e:
        logger.warning(f"Milestone age curve fit failed: {e}")
        return curve_failed

    if not fit.success:
        return curve_failed

    midpoint, steepness = float(fit.x[0]), float(fit.x[1])
    # A parameter on one of these bounds means the data does not resolve the transition:
    # the fitted parameters are not meaningful, so reject the fit. MAX_STEEPNESS is
    # deliberately not one of them, see its definition above.
    midpoint_on_bound = np.isclose(midpoint, 0.0) or np.isclose(midpoint, max_age)
    if midpoint_on_bound or steepness <= MIN_STEEPNESS * 1.01:
        return curve_failed

    return MilestoneAgeCurve(
        midpoint=midpoint,
        steepness=steepness,
        n_answers=n_answers,
        fit_ok=True,
    )


def milestone_age_curve_from_collection(
    collection: MilestoneAgeScoreCollection | None,
) -> MilestoneAgeCurve | None:
    if collection is None or not collection.curve_fit_ok:
        return None
    return MilestoneAgeCurve(
        midpoint=collection.curve_midpoint,
        steepness=collection.curve_steepness,
        n_answers=collection.curve_n_answers,
        fit_ok=True,
    )


def get_milestone_curves(session: SessionDep) -> dict[int, MilestoneAgeCurve | None]:
    return {
        collection.milestone_id: milestone_age_curve_from_collection(collection)
        for collection in session.exec(select(MilestoneAgeScoreCollection)).all()
    }


def get_admin_settings(session: SessionDep) -> AdminSettings:
    """Get admin settings, creating default if not found."""
    settings = session.exec(select(AdminSettings)).first()
    if not settings:
        # Fallback: create default settings if not found
        settings = AdminSettings(id=1)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


def get_milestone_age_curve_params(session: SessionDep) -> MilestoneAgeCurveParams:
    return get_admin_settings(session).milestone_age_curve_params()


def get_milestone_ages_from_curve(
    curve: MilestoneAgeCurve | None, params: MilestoneAgeCurveParams
) -> tuple[int, int, int] | None:
    if curve is None or not curve.fit_ok:
        return None

    max_age = float(app_settings.MAX_CHILD_AGE_MONTHS)
    expected_age = curve.age_at_mean_answer(params.mean_answer_achieved)
    if expected_age > max_age:
        # the curve does not reach the achieved threshold within the supported age
        # range, so we cannot say at what age this milestone is achieved
        return None
    # a steeper curve reaches both thresholds sooner, so sort rather than assume that
    # the min threshold gives the younger age
    age_min, age_max = sorted(
        (
            curve.age_at_mean_answer(params.mean_answer_relevant_min),
            curve.age_at_mean_answer(params.mean_answer_relevant_max),
        )
    )

    # A steep curve crosses both relevant thresholds within a month or two, which would
    # leave the milestone askable for too short a window. Widening the range here, once
    # the other ages have been determined, is the only thing this does: it never moves
    # the expected age or narrows a range that is already wide enough.
    margin = float(params.min_relevant_age_margin_months)
    age_min = min(age_min, expected_age - margin)
    age_max = max(age_max, expected_age + margin)

    def as_months(age: float) -> int:
        return int(np.clip(round(age), 0, max_age))

    return as_months(expected_age), as_months(age_min), as_months(age_max)


def milestone_age_score_collection_public(
    collection: MilestoneAgeScoreCollection, params: MilestoneAgeCurveParams
) -> MilestoneAgeScoreCollectionPublic:
    ages = get_milestone_ages_from_curve(
        milestone_age_curve_from_collection(collection), params
    )
    expected_age, relevant_age_min, relevant_age_max = (
        ages if ages is not None else (None, None, None)
    )
    return MilestoneAgeScoreCollectionPublic(
        milestone_id=collection.milestone_id,
        expected_age=expected_age,
        relevant_age_min=relevant_age_min,
        relevant_age_max=relevant_age_max,
        curve_midpoint=collection.curve_midpoint,
        curve_steepness=collection.curve_steepness,
        curve_fit_ok=collection.curve_fit_ok,
        curve_n_answers=collection.curve_n_answers,
        scores=collection.scores,
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


def count_users_mondey_data(session: SessionDep, user_id: int) -> dict[str, int]:
    """Count the data a user has in the mondey database, for the deletion dry run."""
    child_ids = session.exec(
        select(Child.id).where(col(Child.user_id) == user_id)
    ).all()
    affected_answers = session.exec(
        select(func.count())
        .select_from(MilestoneAnswer)
        .join(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.user_id) == user_id)
    ).one()
    affected_answers += session.exec(
        select(func.count())
        .select_from(ChildAnswer)
        .where(col(ChildAnswer.child_id).in_(child_ids))
    ).one()
    affected_answers += session.exec(
        select(func.count())
        .select_from(UserAnswer)
        .where(col(UserAnswer.user_id) == user_id)
    ).one()
    return {
        "affectedChildren": len(child_ids),
        "affectedAnswers": affected_answers,
    }


def delete_users_mondey_data(session: SessionDep, user_id: int) -> None:
    child_ids = session.exec(
        select(Child.id).where(col(Child.user_id) == user_id)
    ).all()
    for child_id in child_ids:
        child_image_path(child_id).unlink(missing_ok=True)
    # milestone answers are removed by the cascade from their answer session
    session.execute(
        delete(MilestoneAnswerSession).where(
            (col(MilestoneAnswerSession.user_id) == user_id)
            | (col(MilestoneAnswerSession.child_id).in_(child_ids))
        )
    )
    session.execute(delete(ChildAnswer).where(col(ChildAnswer.child_id).in_(child_ids)))
    session.execute(delete(UserAnswer).where(col(UserAnswer.user_id) == user_id))
    session.execute(delete(Child).where(col(Child.user_id) == user_id))
    session.commit()
