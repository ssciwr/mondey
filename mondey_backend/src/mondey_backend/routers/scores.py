from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import cast

import numpy as np

from ..dependencies import SessionDep
from ..models.children import Child
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScoreCollection
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAgeScore
from ..models.milestones import MilestoneGroupAgeScoreCollection
from .statistics import calculate_milestone_statistics_by_age
from .statistics import calculate_milestonegroup_statistics_by_age
from .utils import get_child_age_in_months


class TrafficLight(Enum):
    """
    Enum for the trafficlight feedback.
    Includes -1 for red,  0 for yellow and 1 is green overall.

    Invalid is -2 and is included for edge cases like no data.
    """

    invalid = -2
    red = -1
    yellow = 0
    green = 1


def compute_feedback_simple(
    stat: MilestoneAgeScore | MilestoneGroupAgeScore,
    score: float,
) -> int:
    """
    Compute trafficlight feedback. Replace this function with your own if you
    want to change the feedback logic.
    Parameters
    ----------
    stat : MilestoneAgeScore | MilestoneGroupAgeScore
        Struct containing the average and standard deviation of the scores for a single milestone
    value : float

    Returns
    -------
    int
        -1 if score <= avg - 2 * stddev (trafficlight: red)
        0 if avg - 2 * stddev < score <= avg - stddev (trafficlight: yellow)
        1if score > avg - stddev (trafficlight: green)
    """

    def leq(val: float, lim: float) -> bool:
        return val < lim or bool(np.isclose(val, lim))

    if stat.avg_score < 1e-2 and stat.stddev_score < 1e-2:
        # statistics has no data
        return TrafficLight.invalid.value

    if stat.stddev_score < 1e-2:
        # statistics data is degenerate and has no variance <- few datapoints
        # in this case, any score below the average is considered underperforming:
        # one step below -> yellow, two steps below -> red
        lim_lower = stat.avg_score - 2
        lim_upper = stat.avg_score - 1
    else:
        lim_lower = stat.avg_score - 2 * stat.stddev_score
        lim_upper = stat.avg_score - stat.stddev_score

    if leq(score, lim_lower):
        return TrafficLight.red.value
    elif score > lim_lower and leq(score, lim_upper):
        return TrafficLight.yellow.value
    else:
        return TrafficLight.green.value


def compute_milestonegroup_feedback_summary(
    session: SessionDep, child_id: int, answersession_id: int
) -> dict[int, int]:
    """
    Compute the summary milestonegroup feedback for a single milestonegroup. This is done
    by first calculating the mean score over all milestones that belong to the milestonegroup that
    are relevant for the child when the given answersession was created. The mean is then
    compared against the mean and standard deviation over the known population of children for the child's age.
    When the statistics is outdated (older than a week currently) or there is none, it is recomputed and updated in the database.
    See `compute_feedback_simple` for the feedback logic.

    Parameters
    ----------
    session : SessionDep
        database session
    child_id : int
        child to compute feedback for. Needed for age computation
    answersession_id : int
        answersession to compute feedback for. This contains the answers on which basis the feedback is computed

    Returns
    -------
    dict[int, int]
        Dictionary of milestonegroup_id -> feedback
    """
    logger = logging.getLogger(__name__)
    logger.debug("compute_milestonegroup_feedback_summary")
    answersession = session.get(MilestoneAnswerSession, answersession_id)

    if answersession is None:
        raise ValueError("No answersession with id: ", answersession_id)
    logger.debug(
        f"  answersession id: {answersession_id}, created_at: {answersession.created_at}"
    )

    # get child age
    child = session.get(Child, child_id)
    if child is None:
        raise ValueError("No child with id: ", child_id)
    age = get_child_age_in_months(child, answersession.created_at)
    logger.debug(f"  child age in months: {age}")
    # extract milestonegroups
    groups = set(answer.milestone_group_id for answer in answersession.answers.values())
    today = datetime.now()

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    # if the statistics is older than a week, we update it with the current data
    feedback: dict[int, int] = {}
    for group in groups:
        logger.debug(f"  group: {group}")
        stats = session.get(MilestoneGroupAgeScoreCollection, group)
        logger.debug(f"  old stats: {stats}")
        if stats is not None:
            for i, score in enumerate(stats.scores):
                if score.count > 0:
                    logger.debug(
                        f"   old score: , {i}, {score.count}, {score.avg_score}, {score.stddev_score}"
                    )

        if stats is None or stats.created_at < today - timedelta(days=7):
            new_stats = calculate_milestonegroup_statistics_by_age(session, group)

            if new_stats is None:
                raise ValueError("No statistics for milestone group: ", group)

            # update stuff in database
            for i, new_score in enumerate(new_stats.scores):
                if new_score.count > 0:
                    logger.debug(
                        f"   new_score: , {i}, {new_score.count}, {new_score.avg_score}, {new_score.stddev_score}"
                    )
                session.merge(new_score)

            session.merge(new_stats)
            session.commit()
            stats = new_stats

        # extract the answers for the current milestone group
        group_answers = [
            answer.answer + 1
            for answer in answersession.answers.values()
            if answer.milestone_group_id == group
        ]
        logger.debug(
            f'  group answers: , {group_answers}, "mean: ", {np.mean(group_answers)}'
        )
        # use the statistics recorded for a certain age as the basis for the feedback computation
        feedback[group] = compute_feedback_simple(
            stats.scores[age], float(np.mean(group_answers))
        )
    logger.debug(f"summary feedback: {feedback}")
    return feedback


def compute_milestonegroup_feedback_detailed(
    session: SessionDep, child_id: int, answersession_id: int
) -> dict[int, dict[int, int]]:
    """
    Compute the per-milestone (detailed) feedback for all answers in a given answersession.
    This is done by comparing the given answer per milestone against the mean and standard deviation of the known population of children for the child's age. If this statistics is outdated (older than a week currently) or is
    missing, it is recomputed and updated in the database. See `compute_feedback_simple` for the feedback logic.
    Return a dictionary mapping milestonegroup -> [milestone -> feedback].
    Parameters
    ----------
    session : SessionDep
        database session
    child_id : int
        child to compute feedback for. Needed for age computation
    answersession_id : int
        answersession to compute feedback for. This contains the answers on which basis the feedback is computed

    Returns
    -------
    dict[int, dict[int, int]]
        Dictionary of milestonegroup_id -> [milestone_id -> feedback]
    """
    logger = logging.getLogger(__name__)

    logger.debug("compute_milestonegroup_feedback_detailed")
    answersession = session.get(MilestoneAnswerSession, answersession_id)

    if answersession is None:
        raise ValueError("No answersession with id: ", answersession_id)
    logger.debug(
        f"  answersession id: {answersession_id} created_at: {answersession.created_at}"
    )
    # get child age
    child = session.get(Child, child_id)

    if child is None:
        raise ValueError("No child with id: ", child_id)

    age = get_child_age_in_months(child, answersession.created_at)
    logger.debug(f"  child age in months: {age}")
    today = datetime.today()

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, dict[int, int]] = {}
    for milestone_id, answer in answersession.answers.items():
        # try to get statistics for the current milestone and update it if it's not there
        # or is too old
        stats = session.get(MilestoneAgeScoreCollection, milestone_id)
        logger.debug(f"  old stats: {stats}")
        if stats is not None:
            for i, score in enumerate(stats.scores):
                if score.count > 0:
                    logger.debug(
                        f"   old score: {i}, {score.count}, {score.avg_score}, {score.stddev_score}"
                    )

        if stats is None or stats.created_at < today - timedelta(days=7):
            new_stats = calculate_milestone_statistics_by_age(session, milestone_id)

            if new_stats is None:
                raise ValueError(
                    "No new statistics could be calculated for milestone: ",
                    milestone_id,
                )

            # update stuff in database
            for i, new_score in enumerate(new_stats.scores):
                if new_score.count > 0:
                    logger.debug(
                        f"   new_score: , {i}, {new_score.count}, {new_score.avg_score}, {new_score.stddev_score}"
                    )
                session.merge(new_score)

            session.merge(new_stats)
            session.commit()
            stats = new_stats

        if answer.milestone_group_id not in feedback:
            feedback[answer.milestone_group_id] = {}

        feedback[answer.milestone_group_id][cast(int, answer.milestone_id)] = (
            compute_feedback_simple(stats.scores[age], answer.answer + 1)
        )

    logger.debug(f" detailed feedback: {feedback}")

    return feedback
