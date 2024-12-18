from __future__ import annotations

import datetime
from collections.abc import Sequence

import numpy as np
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
# we are using Welford's method here. This necessitates recording the count.
def _add_sample(
    count: int,
    mean: float | int,
    m2: float | int,
    new_value: float | int,
) -> tuple[int, float | int, float | int]:
    """
    Add a sample to the the current statistics. This function uses an online algorithm to compute the mean (directly) and an intermediate for the variance. This uses Welford's method with a slight
    modification to avoid numerical instability. See https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
    for details.

    Parameters
    ----------
    count : int
        number of samples added so far.
    mean : float | int
        current mean of the samples.
    m2 : float | int
        intermediate value for the variance computation.
    new_value : float | int
        new sample to be added to the statistics.

    Returns
    -------
    tuple[float | int, float | int, float | int]
        updated count, mean, and m2 values.
    """
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
    """
    Compute the mean and standard deviation from the intermediate values. This function is used to finalize the statistics after a batch of new samples have been added. If arrays are supplied, they all need to have the
    same shape. Values for the standard deviation for which the count is less than 2 are set to zero.

    Parameters
    ----------
    count : int | np.ndarray
        Current counts of samples. If ndarray, it contains the number of samples for each entry.
    mean : float | int | np.ndarray
        Current mean value of the samples. If ndarray, it contains the mean for each entry.
    m2 : float | int | np.ndarray
        Current intermediate value for variance computation. If ndarray, it contains the intermediate value for each entry.

    Returns
    -------
    tuple[float | int | np.ndarray, float | np.ndarray, float | np.ndarray]
        updated count, mean, and standard deviation values.

    Raises
    ------
    ValueError
        If arguments of incompatible types are given

    ValueError
        If arrays have different shapes.
    """
    if all(isinstance(x, float | int) for x in [count, mean, m2]):
        if count < 2:
            return count, mean, 0.0
        else:
            var = m2 / (count - 1)
            return count, mean, np.sqrt(var)
    elif all(isinstance(x, np.ndarray) for x in [count, mean, m2]):
        if not all(x.shape == count.shape for x in [mean, m2]):  # type: ignore
            raise ValueError(
                "Given arrays for statistics computation must have the same shape."
            )

        with np.errstate(invalid="ignore"):
            valid_counts = count >= 2
            variance = m2
            variance[valid_counts] /= count[valid_counts] - 1  # type: ignore
            variance[np.invert(valid_counts)] = 0.0  # type: ignore
            return (
                count,
                np.nan_to_num(mean),
                np.nan_to_num(np.sqrt(variance)),
            )  # get stddev
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
    """
    Calculate mean and variance for a set of answers by age in months. Makes use of an online
    algorithm for variance and mean calculation that updates preexisting statistics with the
    values provided in the answers.

    Parameters
    ----------
    answers : Sequence[MilestoneAnswer]
        Answers to include in the statistics.
    child_ages : dict[int, int]
        Dictionary of answer_session_id -> age in months.
    count : np.ndarray | None, optional
        Number of elements from which the current statistics is built, by default None.
        Will be initialized as a zero array if None.
    avg : np.ndarray | None, optional
        Current mean values per age, by default None.
        Will be initialized as a zero array if None.
    stddev : np.ndarray | None, optional
        Current standard deviation values per age, by default None.
        Will be initialized as a zero array if None.
    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Updated count, avg and stddev arrays.
    """
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
    session: SessionDep,
    milestone_id: int,
) -> MilestoneAgeScoreCollection | None:
    """
    Calculate the mean, variance of a milestone per age in months.
    Takes into account only answers from expired sessions. If no statistics exist yet, all answers from expired sessions are considered, else only the ones newer than the last statistics are considered.

    Parameters
    ----------
    session : SessionDep
        database session
    milestone_id : int
        id of the milestone to calculate the statistics for
    Returns
    -------
    MilestoneAgeScoreCollection | None
        MilestoneAgeScoreCollection object which contains a list of MilestoneAgeScore objects,
    one for each month, or None if there are no answers for the milestoneg and no previous statistics.
    """
    session_expired_days: int = 7

    # get the newest statistics for the milestone
    last_statistics = session.get(MilestoneAgeScoreCollection, milestone_id)

    # initialize avg and stddev scores with the last known statistics or to None if no statistics are available
    child_ages = _get_answer_session_child_ages_in_months(session)
    expiration_date = datetime.datetime.now() - datetime.timedelta(
        days=session_expired_days
    )

    count = None
    avg_scores = None
    stddev_scores = None

    if last_statistics is None:
        # no statistics exists yet -> all answers from expired sessions are relevant

        answers_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                col(MilestoneAnswer.answer_session_id) == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_id == milestone_id)
            .where(~col(MilestoneAnswer.included_in_milestone_statistics))
            .where(MilestoneAnswerSession.created_at < expiration_date)
        )
    else:
        # initialize avg and stddev scores with the last known statistics
        last_scores = last_statistics.scores
        count = np.array([score.count for score in last_scores])
        avg_scores = np.array([score.avg_score for score in last_scores])
        stddev_scores = np.array([score.stddev_score for score in last_scores])

        # we calculate the statistics with an online algorithm, so we only consider new data
        # that has not been included in the last statistics but which stems from sessions that are expired
        answers_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                col(MilestoneAnswer.answer_session_id) == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_id == milestone_id)
            .where(~col(MilestoneAnswer.included_in_milestone_statistics))
            .where(col(MilestoneAnswerSession.created_at) <= expiration_date)
        )

    answers = session.exec(answers_query).all()

    for answer in answers:
        answer.included_in_milestone_statistics = True
        session.merge(answer)
    session.commit()

    if len(answers) == 0:
        # return last statistics if no new answers are available, because that is the best we can do then.
        return last_statistics
    else:
        count, avg_scores, stddev_scores = _get_statistics_by_age(
            answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
        )

        expected_age = _get_expected_age_from_scores(avg_scores)

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
    session: SessionDep,
    milestonegroup_id: int,
) -> MilestoneGroupAgeScoreCollection | None:
    """
    Calculate the mean, variance of a milestonegroup per age in months.
    Takes into account only answers from expired sessions. If no statistics exist yet, all answers from expired sessions are considered, else only the ones newer than the last statistics are considered.

    Parameters
    ----------
    session : SessionDep
        database session
    milestonegroup_id : int
        id of the milestonegroup to calculate the statistics for

    Returns
    -------
    MilestoneGroupAgeScoreCollection | None
        MilestoneGroupAgeScoreCollection object which contains a list of MilestoneGroupAgeScore objects,
    one for each month, or None if there are no answers for the milestonegroup and no previous statistics.
    """

    session_expired_days: int = 7

    # get the newest statistics for the milestonegroup
    last_statistics = session.get(MilestoneGroupAgeScoreCollection, milestonegroup_id)

    child_ages = _get_answer_session_child_ages_in_months(session)
    expiration_date = datetime.datetime.now() - datetime.timedelta(
        days=session_expired_days
    )

    count = None
    avg_scores = None
    stddev_scores = None
    # we have 2 kinds of querys that need to be executed depending on the existence of a statistics object
    if last_statistics is None:
        # no statistics exists yet -> all answers from expired sessions are relevant
        answer_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                col(MilestoneAnswer.answer_session_id) == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_group_id == milestonegroup_id)
            .where(~col(MilestoneAnswer.included_in_milestonegroup_statistics))
            .where(
                MilestoneAnswerSession.created_at
                <= expiration_date  # expired session only
            )
        )
    else:
        # initialize avg and stddev scores with the last known statistics
        count = np.array(
            [score.count for score in last_statistics.scores], dtype=np.int32
        )
        avg_scores = np.array(
            [score.avg_score for score in last_statistics.scores], dtype=np.float64
        )
        stddev_scores = np.array(
            [score.stddev_score for score in last_statistics.scores]
        )
        # we calculate the statistics with an online algorithm, so we only consider new data
        # that has not been included in the last statistics but which stems from sessions that are expired
        # README: same reason for type: ignore as in the function above
        answer_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                col(MilestoneAnswer.answer_session_id) == MilestoneAnswerSession.id,
            )
            .where(MilestoneAnswer.milestone_group_id == milestonegroup_id)
            .where(~col(MilestoneAnswer.included_in_milestonegroup_statistics))
            .where(MilestoneAnswerSession.created_at <= expiration_date)
        )

    answers = session.exec(answer_query).all()

    # update answer.included_in_milestonegroup_statistics to True
    for answer in answers:
        answer.included_in_milestonegroup_statistics = True
        session.merge(answer)
    session.commit()

    if len(answers) == 0:
        # return last statistics if no new answers are available, because that is the best we can do then.

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
