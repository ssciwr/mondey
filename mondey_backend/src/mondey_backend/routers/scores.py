from __future__ import annotations

from collections import defaultdict
from enum import Enum

import numpy as np
from sqlmodel import select

from ..dependencies import SessionDep
from ..logging import logger
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScoreCollection
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAgeScore
from ..models.milestones import MilestoneGroupAgeScoreCollection
from .utils import get_answer_session_child_age_in_months


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
        -2 if there is insufficient data to provide feedback (trafficlight: invalid)
        -1 if score <= avg - 2 * stddev (trafficlight: red)
        0 if avg - 2 * stddev < score <= avg - stddev (trafficlight: yellow)
        1 if score > avg - stddev (trafficlight: green)
    """

    def leq(val: float, lim: float) -> bool:
        return val < lim or bool(np.isclose(val, lim))

    if stat.stddev_score < 0:
        # negative stddev indicates insufficient data so we cannot provide feedback
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
    session: SessionDep, answersession: MilestoneAnswerSession
) -> dict[int, int]:
    """
    Compute the summary milestonegroup feedback for each milestonegroup.
    This is done by first calculating the mean score over all milestones that belong to the milestonegroup.
    If a milestone from the group is not included in the answer session then a score is inferred:
      * 0 if the child is younger than the expected age of the milestone
      * 3 if the child is older than the expected age of the milestone
    The mean is then compared against the mean and standard deviation of scores for this milestone group over the
    known population of children for the child's age.
    See `compute_feedback_simple` for the feedback logic.

    Parameters
    ----------
    session : SessionDep
        database session
    answersession : MilestoneAnswerSession
        answersession to compute feedback for. This contains the answers on which basis the feedback is computed

    Returns
    -------
    dict[int, int]
        Dictionary of milestonegroup_id -> feedback
    """
    logger.debug("compute_milestonegroup_feedback_summary")
    logger.debug(
        f"  answersession id: {answersession.id}, created_at: {answersession.created_at}"
    )

    child_age = get_answer_session_child_age_in_months(session, answersession)
    logger.debug(f"  child age in months: {child_age}")

    # get answers for each MilestoneGroup
    milestones = session.exec(select(Milestone)).all()
    milestone_group_answers: dict[int, list[int]] = defaultdict(list)
    for milestone in milestones:
        # if a milestone is not included in the answer session,
        # assume full score if child is older than the expected age for the milestone,
        # and assume zero score if child is younger than the expected age
        answer = answersession.answers.get(milestone.id)  # type: ignore
        score_if_missing = 3 if milestone.expected_age_months < child_age else 0
        milestone_group_answers[milestone.group_id].append(  # type: ignore
            answer.answer if answer is not None else score_if_missing
        )

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    answersession_groups = set(
        answer.milestone_group_id for answer in answersession.answers.values()
    )
    feedback: dict[int, int] = {}
    for group, scores in milestone_group_answers.items():
        logger.debug(f"  group: {group}")
        logger.debug(f"  scores: {scores}")
        avg_score = float(np.mean(scores))
        logger.debug(f"  mean: {avg_score}")
        stats = session.get(MilestoneGroupAgeScoreCollection, group)
        if group in answersession_groups:
            # only provide feedback for a milestonegroup if the answer session contains at least one milestone in the group
            if stats is None:
                logger.debug("  no stats")
                feedback[group] = TrafficLight.invalid.value
            else:
                logger.debug(f"  stats: {stats.scores[child_age]}")
                feedback[group] = compute_feedback_simple(
                    stats.scores[child_age], avg_score
                )
    logger.debug(f"summary feedback: {feedback}")
    return feedback


def compute_milestonegroup_feedback_detailed(
    session: SessionDep, answersession: MilestoneAnswerSession
) -> dict[int, dict[int, int]]:
    """
    Compute the per-milestone (detailed) feedback for all answers in a given answersession.
    This is done by comparing the given answer for a milestone against the mean and standard deviation of the
    known population of children for the child's age.
    See `compute_feedback_simple` for the feedback logic.
    Return a dictionary mapping milestonegroup_id -> [milestone_id -> feedback].
    Parameters
    ----------
    session : SessionDep
        database session
    answersession : MilestoneAnswerSession
        answersession to compute feedback for. This contains the answers on which basis the feedback is computed

    Returns
    -------
    dict[int, dict[int, int]]
        Dictionary of milestonegroup_id -> [milestone_id -> feedback]
    """
    logger.debug("compute_milestonegroup_feedback_detailed")
    logger.debug(
        f"  answersession id: {answersession.id} created_at: {answersession.created_at}"
    )
    child_age = get_answer_session_child_age_in_months(session, answersession)
    logger.debug(f"  child age in months: {child_age}")

    # for each milestone in the answer session, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, dict[int, int]] = defaultdict(dict)
    for milestone_id, answer in answersession.answers.items():
        logger.debug(f"  milestone_id: {milestone_id}, answer: {answer.answer}")
        stats = session.get(MilestoneAgeScoreCollection, milestone_id)
        if stats is None:
            logger.debug("    -> no stats")
            feedback_value = TrafficLight.invalid.value
        else:
            feedback_value = compute_feedback_simple(
                stats.scores[child_age], answer.answer
            )
            logger.debug(
                f"    -> avg: {stats.scores[child_age].avg_score}, stddev: {stats.scores[child_age].stddev_score}, feedback: {feedback_value}"
            )
        feedback[answer.milestone_group_id][answer.milestone_id] = feedback_value  # type: ignore

    logger.debug(f" detailed feedback: {feedback}")

    return feedback
