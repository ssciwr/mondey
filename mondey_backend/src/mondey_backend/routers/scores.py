from __future__ import annotations

import logging
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

    logging.warning(f"Score was {score}")
    if stat.avg_score < 1e-2 and stat.stddev_score < 1e-2:
        # statistics has no data
        return TrafficLight.invalid.value

    if stat.stddev_score < 1e-2:
        logging.warning("Score was degenerate statistically")
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
        # If the score is less than the average score - 1, we get yellow.
        # So a score of average-0.8 gets green by falling into the else below.
    elif (
        score == 1
    ):  # Specifically marked as not having acheived the milestone ("Gar nichts").
        # Even if the stats are degenerate (so lim_lower and upper will be below 0), return yellow.
        logging.warning("Default yellow case")
        return TrafficLight.yellow.value
    else:
        logging.warning(f"Default green case, score was {score}")
        return TrafficLight.green.value


def compute_milestonegroup_feedback_summary(
    session: SessionDep, child_id: int, answersession_id: int
) -> dict[int, int]:
    """
    Compute the summary milestonegroup feedback for a single milestonegroup. This is done
    by first calculating the mean score over all milestones that belong to the milestonegroup that
    are relevant for the child when the given answersession was created. The mean is then
    compared against the mean and standard deviation over the known population of children for the child's age.
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

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, int] = {}
    for group in groups:
        logger.debug(f"  group: {group}")
        stats = session.get(MilestoneGroupAgeScoreCollection, group)
        if stats is None:
            logger.debug("  no stats")
            feedback[group] = TrafficLight.invalid.value
        else:
            logger.debug(f"  stats: {stats}")
            for i, score in enumerate(stats.scores):
                if score.count > 0:
                    logger.debug(
                        f"   score: , {i}, {score.count}, {score.avg_score}, {score.stddev_score}"
                    )
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
    This is done by comparing the given answer per milestone against the mean and standard deviation of the known population of children for the child's age.
    See `compute_feedback_simple` for the feedback logic.
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

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, dict[int, int]] = {}
    for milestone_id, answer in answersession.answers.items():
        logging.warning("")
        logging.warning("")
        logger.warning(
            f"  milestone id: {milestone_id}, this specific childs answer: {answer.answer + 1}"
        )
        stats = session.get(MilestoneAgeScoreCollection, milestone_id)
        logger.warning(f"  stats: {stats}")
        if answer.milestone_group_id not in feedback:
            logger.warning("Group ID not in 'feedback' variable.")
            feedback[answer.milestone_group_id] = {}
        if stats is None:
            logger.warning("Feedback was None because stats was none!")
            feedback[answer.milestone_group_id][cast(int, answer.milestone_id)] = (
                TrafficLight.invalid.value
            )
        else:
            for i, score in enumerate(stats.scores):
                if score.count > 0:
                    logger.debug(
                        f"   score: {i}, {score.count}, {score.avg_score}, {score.stddev_score}"
                    )
            traffic_light_answer_value = compute_feedback_simple(
                stats.scores[age], answer.answer + 1
            )
            feedback[answer.milestone_group_id][cast(int, answer.milestone_id)] = (
                traffic_light_answer_value
            )
            logger.warning(f"Score at age: {stats.scores[age]}")
            logger.warning(f"Answer: {answer.answer + 1}")
            logger.warning(
                f"Converted to Traffic Light Output Answer: {traffic_light_answer_value}"
            )
            # logger.warning(str(compute_feedback_simple(stats.scores[age], answer.answer + 1)))

    logger.warning(f" detailed feedback: {feedback}")

    return feedback
