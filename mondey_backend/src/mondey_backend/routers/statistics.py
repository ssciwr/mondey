from __future__ import annotations

import datetime
from collections.abc import Sequence

import numpy as np
from sqlmodel import col
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScoreCollection
from ..models.milestones import MilestoneAnswer
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAgeScore
from ..models.milestones import MilestoneGroupAgeScoreCollection
from .utils import _get_answer_session_child_ages_in_months
from .utils import _get_expected_age_from_scores
from .utils import add


# see: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
# reason for not using existing package: bessel correction usually not respected
# we are using Welford's method here. This necessitates recording the count
def _add_sample(
    count: int,
    mean: float,
    m2: float,
    new_value: float,
) -> tuple[int, float, float]:
    count += 1
    delta = new_value - mean
    mean += delta / count
    delta2 = new_value - mean
    m2 += delta * delta2
    return count, mean, m2


def _finalize_statistics(
    count: int | np.ndarray[int],
    mean: float | np.ndarray[float],
    m2: float | np.ndarray[float],
) -> tuple[int | np.ndarray[int], float | np.ndarray[float], float | np.ndarray[float]]:
    if isinstance(count, int):
        if count < 2:
            return count, mean, 0.0
        else:
            variance = m2 / (count - 1)
            return count, mean, np.sqrt(variance)
    elif isinstance(count, np.ndarray):
        with np.errstate(invalid="ignore"):
            valid_counts = count >= 2
            variance = m2
            variance[valid_counts] /= count[valid_counts] - 1
            variance[not valid_counts] = 0.0
            return count, np.nan_to_num(mean), np.nan_to_num(np.sqrt(variance))
    else:
        raise ValueError("given values must be of type int|float|np.ndarray")


def _get_statistics_by_age(
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    count: np.ndarray = None,
    avg: np.ndarray = None,
    stddev: np.ndarray = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if count is None or avg is None or stddev is None:
        max_age_months = 72
        count = np.zeros(max_age_months + 1)
        avg = np.zeros(max_age_months + 1)
        stddev = np.zeros(max_age_months + 1)

    # online algorithm computes variance, so need to square stddev first
    var = stddev**2

    if child_ages == {}:
        return count, avg, stddev

    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        new_count, new_avg, new_var = _add_sample(
            count[age], avg[age], var[age], answer.answer + 1
        )
        count[age] = new_count
        avg[age] = new_avg
        var[age] = new_var

    count, avg, stddev = _finalize_statistics(count, avg, var)

    return count, avg, stddev


def calculate_milestone_statistics_by_age(
    session: SessionDep,
    milestone_id: int,
) -> MilestoneAgeScoreCollection:
    """
    _summary_

    Parameters
    ----------
    session : SessionDep
        _description_
    milestone_id : int
        _description_
    answers : Sequence[MilestoneAnswer] | None, optional
        _description_, by default None

    Returns
    -------
    MilestoneAgeScoreCollection
        _description_
    """
    # get the newest statistics for the milestone
    last_statistics = session.exec(
        select(MilestoneAgeScoreCollection)
        .where(col(MilestoneAgeScoreCollection.milestone_id) == milestone_id)
        .order_by(MilestoneAgeScoreCollection.created_at.desc())
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

    if last_statistics is None:
        answers_query = select(MilestoneAnswer).where(
            MilestoneAnswer.milestone_id == milestone_id
        )
    else:
        answers_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(
                MilestoneAnswer.milestone_id == milestone_id,
                MilestoneAnswerSession.created_at > last_statistics.created_at,
            )
        )
    answers = session.exec(answers_query).all()

    count, avg, stddev = _get_statistics_by_age(
        answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
    )
    expected_age = _get_expected_age_from_scores(avg)
    new_id = last_statistics.id + 1 if last_statistics is not None else 1
    return MilestoneAgeScoreCollection(
        id=new_id,
        milestone_id=milestone_id,
        expected_age=expected_age,
        created_at=datetime.datetime.now(),
        scores=[
            MilestoneAgeScore(
                collection_id=new_id,
                count=count[age],
                avg_score=avg[age],
                stddev_score=stddev[age],
                age_months=age,
                expected_score=4
                if age >= expected_age
                else 1,  # TODO: placeholder algorithm? how does the model behind this look like really?
            )
            for age in range(0, len(avg))
        ],
    )


def calculate_milestonegroup_statistics_by_age(
    session: SessionDep,
    milestonegroup_id,
) -> MilestoneGroupAgeScoreCollection:
    """
    _summary_

    Parameters
    ----------
    session : SessionDep
        _description_
    milestonegroup_id : _type_
        _description_
    answers : Sequence[MilestoneAnswer] | None, optional
        _description_, by default None

    Returns
    -------
    MilestoneGroupAgeScoreCollection
        _description_
    """

    # get the newest statistics for the milestonegroup
    last_statistics = session.exec(
        select(MilestoneGroupAgeScoreCollection)
        .where(
            col(MilestoneGroupAgeScoreCollection.milestonegroup_id) == milestonegroup_id
        )
        .order_by(MilestoneGroupAgeScoreCollection.created_at.desc())
    ).first()

    count = None
    avg_scores = None
    stddev_scores = None
    if last_statistics is None:
        max_age_months = 72
        count = np.zeros(max_age_months + 1)
        avg_scores = np.zeros(max_age_months + 1)
        stddev_scores = np.zeros(max_age_months + 1)
    else:
        count = np.array([score.count for score in last_statistics.scores])
        avg_scores = np.array([score.avg_score for score in last_statistics.scores])
        stddev_scores = np.array(
            [score.stddev_score for score in last_statistics.scores]
        )

    child_ages = _get_answer_session_child_ages_in_months(session)

    if last_statistics is None:
        answer_query = select(MilestoneAnswer).where(
            col(MilestoneAnswer.milestone_group_id) == milestonegroup_id
        )
    else:
        answer_query = (
            select(MilestoneAnswer)
            .join(
                MilestoneAnswerSession,
                MilestoneAnswer.answer_session_id == MilestoneAnswerSession.id,
            )
            .where(
                MilestoneAnswer.milestone_group_id == milestonegroup_id,
                MilestoneAnswerSession.created_at > last_statistics.created_at,
            )
        )

    answers = session.exec(answer_query).all()

    count, avg, stddev = _get_statistics_by_age(
        answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
    )
    new_id = last_statistics.id + 1 if last_statistics is not None else 1
    return MilestoneGroupAgeScoreCollection(
        id=new_id,
        milestonegroup_id=milestonegroup_id,
        scores=[
            MilestoneGroupAgeScore(
                collection_id=new_id,
                age_months=age,
                count=count[age],
                avg_score=avg[age],
                stddev_score=stddev[age],
                milestonegroup_id=milestonegroup_id,
            )
            for age in range(0, len(avg))
        ],
        created_at=datetime.datetime.now(),
    )


def recompute_milestonegroup_statistics(session: SessionDep):
    # fetch all milestonegroup statsitcs and check how old they are. Then
    # recompute the ones that are older than timedelta and put back into database
    # do the same for milestone statistics

    milestonegroups = session.exec(select(MilestoneGroup.id)).all()
    for milestonegroup in milestonegroups:
        statistics = calculate_milestonegroup_statistics_by_age(session, milestonegroup)
        for score in statistics.scores:
            add(session, score)
        add(session, statistics)


def recompute_milestone_statistics(session: SessionDep):
    # fetch all milestonegroup statsitcs and check how old they are. Then
    # recompute the ones that are older than timedelta and put back into database
    # do the same for milestone statistics

    milestones = session.exec(select(Milestone.id)).all()
    for milestone in milestones:
        statistics = calculate_milestone_statistics_by_age(session, milestone)  # type: ignore
        for score in statistics.scores:
            add(session, score)
        add(session, statistics)
