from __future__ import annotations

from collections import defaultdict
from enum import Enum

import numpy as np
from sqlmodel import select

from ..dependencies import SessionDep
from ..logging import logger
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroupAgeScore
from .utils import get_answer_session_child_age_in_months
from .utils import get_milestone_curves
from .utils import get_previously_achieved_milestone_ids


class TrafficLight(Enum):
    """
    Enum for the trafficlight feedback.
    Includes -1 for red, 0 for yellow and 1 is green overall.

    Invalid is -2 and is included for edge cases like no data.
    """

    invalid = -2
    red = -1
    yellow = 0
    green = 1


def compute_feedback_milestone(
    milestone: Milestone | None, child_age: int, answer: int
) -> int:
    """
    Trafficlight feedback for milestones.
    If a child is old enough that the milestone is expected to be achieved, an answer of 0 is considered red,
    an answer of 1 is considered yellow, and an answer of 2 or 3 is considered green.
    If the child is younger than the expected age for the milestone, the feedback is always green.
    Parameters
    ----------
    milestone : Milestone | None
        The milestone to compute feedback for
    child_age : int
        The age of the child in months
    answer : int
        The score to compute feedback for

    Returns
    -------
    int
        -2 if there is insufficient data to provide feedback (trafficlight: invalid)
        -1 if answer is 0 and child is not younger than the expected age (trafficlight: red)
        0 if answer is 1 and child is not younger than the expected age (trafficlight: yellow)
        1 otherwise (trafficlight: green)
    """

    if milestone is None:
        return TrafficLight.invalid.value
    if child_age < milestone.expected_age_months:
        return TrafficLight.green.value
    if answer == 0:
        return TrafficLight.red.value
    if answer == 1:
        return TrafficLight.yellow.value
    return TrafficLight.green.value


def compute_feedback_milestone_group(
    stats: MilestoneGroupAgeScore | None, score: float
) -> int:
    """
    Trafficlight feedback for milestone groups.
    Parameters
    ----------
    stats : MilestoneGroupAgeScore
        Contains the average and standard deviation of the scores for this milestone group and age
    score : float
        The score to compare against stats

    Returns
    -------
    int
        -2 if there is insufficient data to provide feedback (trafficlight: invalid)
        -1 if score < avg - 2 * stddev (trafficlight: red)
        0 if avg - 2 * stddev <= score < avg - stddev (trafficlight: yellow)
        1 if score >= avg - stddev (trafficlight: green)
    """

    min_num_samples = 5
    if stats is None or stats.count < min_num_samples:
        return TrafficLight.invalid.value
    mean = stats.mean
    stddev = stats.stddev
    delta_stddevs = (score - mean) / stddev
    logger.debug(
        f"  score: {score}, mean: {mean}, stddev: {stddev}, delta_stddevs: {delta_stddevs}"
    )
    if delta_stddevs < -2:
        return TrafficLight.red.value
    elif delta_stddevs < -1:
        return TrafficLight.yellow.value
    else:
        return TrafficLight.green.value


def compute_milestonegroup_feedback_summary(
    session: SessionDep, answersession: MilestoneAnswerSession
) -> dict[int, int]:
    """
    Compute the summary milestonegroup feedback for each milestonegroup.
    This is done by first calculating the mean score over the milestones that belong to the
    milestonegroup and have a fitted age curve (see `fit_milestone_age_curve`). If such a
    milestone is not included in the answer session then a score is inferred for it:
      * 3 if the child already achieved it in an earlier answer session, which is why it is
        no longer being asked about
      * otherwise the mean answer of children of this age for that milestone, from its
        fitted age curve
    This has to match how the milestone group statistics are calculated in
    `async_update_stats`, since the mean is then compared against the mean and standard
    deviation of scores for this milestone group over the known population of children for
    the child's age.
    See `compute_feedback_milestone_group` for the feedback logic.

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
    milestone_group_answers: dict[int, list[float]] = defaultdict(list)
    milestone_group_ids = set()
    achieved_milestone_ids = get_previously_achieved_milestone_ids(
        session, answersession.child_id, answersession.created_at
    )
    milestone_curves = get_milestone_curves(session)
    for milestone in milestones:
        answer = answersession.answers.get(milestone.id)  # type: ignore
        if answer is not None:
            # only provide feedback for a milestone group if the answer session contains at least one milestone in the group
            milestone_group_ids.add(answer.milestone_group_id)
        # this score is compared against the milestone group statistics, so it has to be
        # calculated over the same milestones that those are calculated over: the ones
        # with a fitted age curve.
        curve = milestone_curves.get(milestone.id)  # type: ignore
        if curve is None:
            continue
        if answer is not None:
            answer_value = float(answer.answer)
        elif milestone.id in achieved_milestone_ids:
            # the child achieved this milestone in an earlier session, which is why it is
            # not in this one - we know the answer, so we do not impute it
            answer_value = 3.0
        else:
            # the child was not asked about this milestone, so impute the mean answer of
            # children of this age for it
            answer_value = float(curve.mean_answer(child_age))
        milestone_group_answers[milestone.group_id].append(answer_value)  # type: ignore

    feedback: dict[int, int] = {}
    for milestone_group_id in milestone_group_ids:
        logger.debug(f"  milestone_group_id: {milestone_group_id}")
        answers = milestone_group_answers[milestone_group_id]
        logger.debug(f"  answers: {answers}")
        if not answers:
            # no milestone in this group has a usable age curve, so there is no score to
            # compare against the statistics for this group
            feedback[milestone_group_id] = TrafficLight.invalid.value
            continue
        avg_score = float(np.mean(answers))
        logger.debug(f"  mean: {avg_score}")
        milestone_group_age_score = session.get(
            MilestoneGroupAgeScore,
            {"milestone_group_id": milestone_group_id, "age": child_age},
        )
        logger.debug(f"  stats: {milestone_group_age_score}")
        feedback[milestone_group_id] = compute_feedback_milestone_group(
            milestone_group_age_score, avg_score
        )
    logger.debug(f"summary feedback: {feedback}")
    return feedback


def compute_milestonegroup_feedback_detailed(
    session: SessionDep, answersession: MilestoneAnswerSession
) -> dict[int, dict[int, int]]:
    """
    Compute the per-milestone (detailed) feedback for all answers in a given answersession.
    See `compute_feedback_milestone` for the feedback logic.
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
        milestone = session.get(Milestone, milestone_id)
        feedback_value = compute_feedback_milestone(milestone, child_age, answer.answer)
        feedback[answer.milestone_group_id][answer.milestone_id] = feedback_value  # type: ignore
    logger.debug(f" detailed feedback: {feedback}")

    return feedback
