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
        -1 if score <= avg - 2 * stddev (trafficlight: red)
        0 if avg - 2 * stddev < score <= avg - stddev (trafficlight: yellow)
        1 if score > avg - stddev (trafficlight: green)
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
    answersession = session.get(MilestoneAnswerSession, answersession_id)
    print("answersession in stat: ", answersession)
    # get child age
    child = session.get(Child, child_id)
    age = get_child_age_in_months(child, answersession.created_at)

    # extract milestonegroups
    groups = set(answer.milestone_group_id for answer in answersession.answers.values())
    today = datetime.now()

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, int] = {}
    print("age: ", age)
    for group in groups:
        print(" current group ", group, "of: ", groups)
        # try to get statistics to use as evaluation basis and recompute if it's not there
        # or is too old
        stats = session.exec(
            select(MilestoneGroupAgeScoreCollection).where(
                MilestoneGroupAgeScoreCollection.milestone_group_id == group
            )
        ).first()

        print(" stats before ", stats)
        print(stats.scores[age])
        print(
            " conditions: ", stats is None, stats.created_at < today - timedelta(days=7)
        )
        print(" created at: ", stats.created_at)
        if stats is None or stats.created_at < today - timedelta(days=7):
            print("recomputing stats")
            new_stats = calculate_milestonegroup_statistics_by_age(session, group)
            # update stuff in database
            for new_score in new_stats.scores:
                print(new_score)
                session.merge(new_score)
            session.merge(new_stats)
            session.commit()
            stats = new_stats
        print(" stats after ", stats)

        # extract the answers for the current milestone group
        group_answers = [
            answer.answer + 1
            for answer in answersession.answers.values()
            if answer.milestone_group_id == group
        ]

        print(
            " group answers: ",
            group_answers,
            np.mean(group_answers),
            min(group_answers),
        )

        # use the statistics recorded for a certain age as the basis for the feedback computation
        feedback[group] = compute_feedback_simple(
            stats.scores[age], np.mean(group_answers), min(group_answers)
        )
    print("feedback: ", feedback)
    return feedback


def compute_milestonegroup_feedback_detailed(
    session: SessionDep, child_id: int, answersession_id: int
) -> dict[int, dict[int, int]]:
    answersession = session.get(MilestoneAnswerSession, answersession_id)
    # get child age
    child = session.get(Child, child_id)
    age = get_child_age_in_months(child, answersession.created_at)
    today = datetime.today()

    # for each milestonegroup, get the statistics, compute the current mean, and compute the feedback
    feedback: dict[int, dict[int, int]] = {}

    for answer in answersession.answers:
        # try to get statistics to use as evaluation basis and recompute if it's not there
        # or is too old
        stats = session.exec(
            select(MilestoneAgeScoreCollection).where(
                MilestoneAgeScoreCollection.milestone_id == answer.milestone_id
            )
        ).first()

        if stats is None or stats.created_at < today - timedelta(days=7):
            stats = calculate_milestonegroup_statistics_by_age(
                session, answer.milestone_group_id
            )
            session.add(stats)

        if answer.milestone_group_id not in feedback:
            feedback[answer.milestone_group_id] = {}

        feedback[answer.milestone_group_id][answer.milestone_id] = (
            compute_feedback_simple(stats.scores[age], answer.answer + 1)
        )
    session.commit()
    return feedback
