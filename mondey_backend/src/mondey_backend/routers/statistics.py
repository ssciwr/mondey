from __future__ import annotations

import datetime
from collections.abc import Sequence

import numpy as np
from sqlalchemy import and_
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScoreCollection
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAgeScore
from ..models.milestones import MilestoneGroupAgeScoreCollection
from .utils import _get_answer_session_child_ages_in_months
from .utils import _get_expected_age_from_scores


# see: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
# reason for not using existing package: bessel correction usually not respected
# we are using Welford's method here. This necessitates recording the count
def _add_sample(
    count: int,
    mean: float | int,
    m2: float | int,
    new_value: float | int,
) -> tuple[float | int, float | int, float | int]:
    count += 1
    delta = new_value - mean
    mean += delta / count
    delta2 = new_value - mean
    m2 += delta * delta2
    return count, mean, m2


def _finalize_statistics(
    count: int | np.ndarray,
    mean: float | int | np.ndarray,
    m2: float | int | np.ndarray,
) -> tuple[float | int | np.ndarray, float | np.ndarray, float | np.ndarray]:
    if all(isinstance(x, float | int) for x in [count, mean, m2]):
        if count < 2:
            return count, mean, 0.0
        else:
            var = m2 / (count - 1)
            return count, mean, np.sqrt(var)
    elif all(isinstance(x, np.ndarray) for x in [count, mean, m2]):
        with np.errstate(invalid="ignore"):
            valid_counts = count >= 2
            variance = m2
            variance[valid_counts] /= count[valid_counts] - 1  # type: ignore
            variance[np.invert(valid_counts)] = 0.0  # type: ignore
            return count, np.nan_to_num(mean), np.nan_to_num(np.sqrt(variance))
    else:
        raise ValueError(
            "Given values for statistics computation must be of type int|float|np.ndarray"
        )


def _get_statistics_by_age(
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    count: np.ndarray | None = None,
    avg: np.ndarray | None = None,
    stddev: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if count is None or avg is None or stddev is None:
        max_age_months = 72
        count = np.zeros(max_age_months + 1, dtype=np.int32)
        avg = np.zeros(max_age_months + 1, dtype=np.float64)
        stddev = np.zeros(max_age_months + 1, dtype=np.float64)

    if child_ages == {}:
        return count, avg, stddev

    # online algorithm computes variance, compute m2 from stddev
    # we can ignore count-1 <= 0 because stddev is zero in this case
    m2 = stddev**2 * (count - 1)

    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        new_count, new_avg, new_m2 = _add_sample(
            count[age], avg[age], m2[age], answer.answer + 1
        )
        count[age] = new_count
        avg[age] = new_avg
        m2[age] = new_m2

    count, avg, stddev = _finalize_statistics(count, avg, m2)  # type: ignore

    return count, avg, stddev


def calculate_milestone_statistics_by_age(
    session: SessionDep, milestone_id: int, session_expired_days: int = 7
) -> MilestoneAgeScoreCollection | None:
    # get the newest statistics for the milestone
    last_statistics = session.exec(
        select(MilestoneAgeScoreCollection)
        .where(col(MilestoneAgeScoreCollection.milestone_id) == milestone_id)
        .order_by(col(MilestoneAgeScoreCollection.created_at).desc())
    ).first()

    # initialize avg and stddev scores with the last known statistics or to None if no statistics are available
    count = None
    avg_scores = None
    stddev_scores = None
    if last_statistics is not None:
        last_scores = last_statistics.scores
        count = np.array([score.count for score in last_scores])
        avg_scores = np.array([score.avg_score for score in last_scores])
        stddev_scores = np.array([score.stddev_score for score in last_scores])

    child_ages = _get_answer_session_child_ages_in_months(session)
    expiration_date = datetime.datetime.now() - datetime.timedelta(
        days=session_expired_days
    )
    # print(' expiration_date: ', expiration_date)
    # print(' last statistics: ', last_statistics)
    if last_statistics is None:
        # no statistics exists yet -> all answers from expired sessions are relevant
        answers_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_id == milestone_id)
            .where(MilestoneAnswerSession.created_at < expiration_date)
        )
    else:
        # we calculate the statistics with an online algorithm, so we only consider new data
        # that has not been included in the last statistics but which stems from sessions that are expired
        answers_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_id == milestone_id)
            .where(
                and_(
                    MilestoneAnswerSession.created_at > last_statistics.created_at,
                    MilestoneAnswerSession.created_at <= expiration_date,
                )  # expired session only which are not in the last statistics
            )
        )

    answers = session.exec(answers_query).all()
    # print('  answers: ', answers)
    if len(answers) == 0:
        return last_statistics
    else:
        count, avg_scores, stddev_scores = _get_statistics_by_age(
            answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
        )

        expected_age = _get_expected_age_from_scores(avg_scores)
        # print(' expected_age: ', expected_age)
        # print(' avg_scores: ', avg_scores)
        # print(' stddev_scores: ', stddev_scores)
        # overwrite last_statistics with updated stuff --> set primary keys explicitly
        return MilestoneAgeScoreCollection(
            milestone_id=milestone_id,
            expected_age=expected_age,
            created_at=datetime.datetime.now(),
            scores=[
                MilestoneAgeScore(
                    age=age,
                    milestone_id=milestone_id,
                    count=int(
                        count[age]
                    ),  # need a conversion to avoid numpy.int32 being stored as byte object
                    avg_score=avg_scores[age],
                    stddev_score=stddev_scores[age],
                    expected_score=4 if age >= expected_age else 1,
                )
                for age in range(0, len(avg_scores))
            ],
        )


def calculate_milestonegroup_statistics_by_age(
    session: SessionDep, milestonegroup_id, session_expired_days: int = 7
) -> MilestoneGroupAgeScoreCollection | None:
    # get the newest statistics for the milestonegroup
    last_statistics = session.exec(
        select(MilestoneGroupAgeScoreCollection)
        .where(
            col(MilestoneGroupAgeScoreCollection.milestone_group_id)
            == milestonegroup_id
        )
        .order_by(col(MilestoneGroupAgeScoreCollection.created_at).desc())
    ).first()

    count = None
    avg_scores = None
    stddev_scores = None
    if last_statistics is not None:
        count = np.array(
            [score.count for score in last_statistics.scores], dtype=np.int32
        )
        avg_scores = np.array(
            [score.avg_score for score in last_statistics.scores], dtype=np.float64
        )
        stddev_scores = np.array(
            [score.stddev_score for score in last_statistics.scores]
        )

    child_ages = _get_answer_session_child_ages_in_months(session)
    expiration_date = datetime.datetime.now() - datetime.timedelta(
        days=session_expired_days
    )
    # print(' expiration_date: ', expiration_date)
    if last_statistics is None:
        # print(' no statistics')
        # no statistics exists yet -> all answers from expired sessions are relevant
        answer_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(col(MilestoneAnswer.milestone_group_id) == milestonegroup_id)
            .where(
                MilestoneAnswerSession.created_at
                < expiration_date  # expired session only
            )
        )
    else:
        # print(' statistics exists')
        # we calculate the statistics with an online algorithm, so we only consider new data
        # that has not been included in the last statistics but which stems from sessions that are expired
        answer_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_group_id == milestonegroup_id)
            .where(
                and_(
                    MilestoneAnswerSession.created_at > last_statistics.created_at,
                    MilestoneAnswerSession.created_at <= expiration_date,
                )
            )  # expired session only which are not in the last statistics
        )
    # all_answers = session.exec(select(MilestoneAnswer)).all()
    # print('weird join: ', session.exec(select(MilestoneAnswer)
    # .join(
    #     MilestoneAnswerSession,
    #     MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
    # )).all())
    # print(' all answers: ', all_answers)
    answers = session.exec(answer_query).all()
    # print(' last statistics: ', last_statistics)
    # print(' relevant answers: ', answers)
    if len(answers) == 0:
        return last_statistics
    else:
        count, avg, stddev = _get_statistics_by_age(
            answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
        )

        return MilestoneGroupAgeScoreCollection(
            milestone_group_id=milestonegroup_id,
            scores=[
                MilestoneGroupAgeScore(
                    milestone_group_id=milestonegroup_id,
                    age=age,
                    count=int(
                        count[age]
                    ),  # need a conversion to avoid numpy.int32 being stored as byte object
                    avg_score=avg[age],
                    stddev_score=stddev[age],
                )
                for age in range(0, len(avg))
            ],
            created_at=datetime.datetime.now(),
        )
