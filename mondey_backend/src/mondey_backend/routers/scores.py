from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from enum import Enum

import numpy as np
from sqlmodel import select

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
    Includes -1 for red, 0 for yellow, and 1 for green.
    Invalid is -2 and is included for edge cases.
    """

    invalid = -3
    red = -2
    yellowWithCaveat = -1
    yellow = 0
    greenWithCaveat = 1
    green = 2


def compute_feedback_simple(
    stat: MilestoneAgeScore | MilestoneGroupAgeScore,
    score: float,
    min_score: float | None = None,
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
        -2 if score <= avg - 2 * stddev (trafficlight: red)
        -1 if 2*stddev < score <= avg - stddev and min < avg - 2*stddev (trafficlight: yellowWithCaveat)
        0 if avg - 2 * stddev < score <= avg - stddev (trafficlight: yellow)
        1 if score > avg - stddev and  avg - 2*stddev < score < avg - stddev (trafficlight: greenWithCaveat)
        2 if score > avg - stddev (trafficlight: green)
    """

    def leq(val: float, lim: float) -> bool:
        return val < lim or np.isclose(val, lim)

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
    print("eval: ", lim_lower, lim_upper, stat.avg_score, score)
    if leq(score, lim_lower):
        return TrafficLight.red.value
    elif score > lim_lower and leq(score, lim_upper):
        if min_score is not None and min_score < lim_lower:
            return TrafficLight.yellowWithCaveat.value
        return TrafficLight.yellow.value
    else:
        if min_score is not None and min_score < lim_upper:
            return TrafficLight.greenWithCaveat.value
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
    answersession = session.get(MilestoneAnswerSession, answersession_id)
    # print('answersession', answersession)
    # print('answers: ', answersession.answers)  
    # get child age
    child = session.get(Child, child_id)
    # print('child', child)
    age = get_child_age_in_months(child, answersession.created_at)
    # print('age ', age)
    # extract milestonegroups
    groups = set(answer.milestone_group_id for answer in answersession.answers.values())
    today = datetime.now()
    # print('groups: ', groups)
    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    # if the statistics is older than a week, we update it with the current data
    feedback: dict[int, int] = {}
    for group in groups:
        # print("current group: ", group)
        stats = session.exec(
            select(MilestoneGroupAgeScoreCollection).where(
                MilestoneGroupAgeScoreCollection.milestone_group_id == group
            )
        ).first()
        # if stats is not None:
            # print('stats before: ', stats, stats.scores[age])
        if stats is None or stats.created_at < today - timedelta(days=7):
            new_stats = calculate_milestonegroup_statistics_by_age(session, group)

            # update stuff in database
            for new_score in new_stats.scores:
                session.merge(new_score)

            session.merge(new_stats)
            session.commit()
            stats = new_stats
        # print('stats after: ', stats, stats.scores[age])
        # extract the answers for the current milestone group
        group_answers = [
            answer.answer + 1
            for answer in answersession.answers.values()
            if answer.milestone_group_id == group
        ]
        # print('group_answers: ', group_answers, stats.scores[age])
        # print('mean: ', np.mean(group_answers))
        # print('min: ', min(group_answers))
        # use the statistics recorded for a certain age as the basis for the feedback computation
        feedback[group] = compute_feedback_simple(
            stats.scores[age], np.mean(group_answers), min(group_answers)
        )
    return feedback


def compute_milestonegroup_feedback_detailed(
    session: SessionDep, child_id: int, answersession_id: int
) -> dict[int, dict[int, int]]:
    """
    Compute the per-milestone (detailed) feedback for all answers in a given answersession. 
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
    answersession = session.get(MilestoneAnswerSession, answersession_id)
    # get child age
    child = session.get(Child, child_id)
    age = get_child_age_in_months(child, answersession.created_at)
    today = datetime.today()
    # print('child: ', child)
    # print('age: ', age)
    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, dict[int, int]] = {}
    for milestone_id, answer in answersession.answers.items():
        # print('current milestone: ', milestone_id, answer)
        # try to get statistics for the current milestone and update it if it's not there
        # or is too old

        stats = session.exec(
            select(MilestoneAgeScoreCollection).where(
                MilestoneAgeScoreCollection.milestone_id == milestone_id
            )
        ).first()
        # print('stats')
        # if stats is not None: 
            # print(' stats before: ', stats, stats.scores[age])

        if stats is None or stats.created_at < today - timedelta(days=7):
            new_stats = calculate_milestone_statistics_by_age(session, milestone_id)
            # update stuff in database
            for new_score in new_stats.scores:
                session.merge(new_score)

            session.merge(new_stats)
            session.commit()
            stats = new_stats

        if answer.milestone_group_id not in feedback:
            feedback[answer.milestone_group_id] = {}

        # print(' stats after: ', stats, stats.scores[age], answer.answer+1)
        feedback[answer.milestone_group_id][answer.milestone_id] = (
            compute_feedback_simple(stats.scores[age], answer.answer + 1)
        )

    return feedback
