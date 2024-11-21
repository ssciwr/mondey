from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

import numpy as np
from sqlmodel import col
from sqlmodel import select

from ..dependencies import CurrentActiveUserDep
from ..dependencies import SessionDep
from ..models.children import Child
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAgeScores
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupStatistics
from .utils import _session_has_expired
from .utils import calculate_milestone_statistics_by_age
from .utils import calculate_milestonegroup_statistics
from .utils import get_child_age_in_months
from .utils import get_db_child


class TrafficLight(Enum):
    """
    Enum for the trafficlight feedback.
    Includes -1 for red, 0 for yellow, and 1 for green.
    Invalid is -2 and is included for edge cases.

    """

    invalid = -2
    red = -1
    yellow = 0
    green = 1


def compute_feedback_simple(
    stat: MilestoneAgeScore | MilestoneGroupStatistics, score: float
) -> int:
    """
    Compute trafficlight feedback. Replace this function with your own if you
    want to change the feedback logic.
    Parameters
    ----------
    stat : MilestoneAgeScore
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

    if stat.stddev_score < 1e-2:
        # README: This happens when all the scores are the same, so any
        # deviation towards lower values can be interpreted as
        # underperformance.
        # This logic relies on the score being integers, such that when the
        # stddev is 0, the avg is an integer
        # TODO: Check again what client wants to happen in such cases
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


def get_milestonegroups_for_answersession(
    session: SessionDep, answersession: MilestoneAnswerSession
) -> Sequence[MilestoneGroup]:
    check_for_overlap = (
        select(Milestone.group_id)
        .where(Milestone.id.in_(answersession.answers.keys()))  # type: ignore
        .distinct()
    )
    return session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id.in_(check_for_overlap))  # type: ignore
    ).all()


def compute_detailed_milestonegroup_feedback_for_answersession(
    session: SessionDep,
    answersession: MilestoneAnswerSession,
    child: Child,
) -> dict[int, dict[int, int]]:
    age = get_child_age_in_months(child, answersession.created_at)
    milestonegroups = get_milestonegroups_for_answersession(session, answersession)

    filtered_answers = {
        m: [
            answersession.answers[ms.id]
            for ms in m.milestones
            if ms.id in answersession.answers and ms.id is not None
        ]
        for m in milestonegroups
    }

    result: dict[int, dict[int, int]] = {}
    statistics: dict[int, MilestoneAgeScores] = {}
    for milestonegroup, answers in filtered_answers.items():
        milestonegroup_result: dict[int, int] = result.get(milestonegroup.id, {})  # type: ignore
        for answer in answers:
            if statistics.get(answer.milestone_id) is None:  # type: ignore
                stat = calculate_milestone_statistics_by_age(
                    session,
                    answer.milestone_id,  # type: ignore
                )  # type: ignore

                statistics[answer.milestone_id] = stat  # type: ignore

            feedback = compute_feedback_simple(
                statistics[answer.milestone_id].scores[age],  # type: ignore
                answer.answer,  # type: ignore
            )  # type: ignore
            milestonegroup_result[answer.milestone_id] = feedback  # type: ignore
        result[milestonegroup.id] = milestonegroup_result  # type: ignore
    return result


def compute_summary_milestonegroup_feedback_for_answersession(
    session: SessionDep,
    answersession: MilestoneAnswerSession,
    child: Child,
    age_limit_low=6,
    age_limit_high=6,
) -> dict[int, int]:
    age = get_child_age_in_months(child, answersession.created_at)

    milestonegroups = get_milestonegroups_for_answersession(session, answersession)

    filtered_answers = {
        m: [
            answersession.answers[ms.id]
            for ms in m.milestones
            if ms.id in answersession.answers and ms.id is not None
        ]
        for m in milestonegroups
    }

    milestone_group_results: dict[int, int] = {}
    for milestonegroup, answers in filtered_answers.items():
        mg_stat = calculate_milestonegroup_statistics(
            session,
            milestonegroup,  # type: ignore
            age,
            age_lower=age - age_limit_low,
            age_upper=age + age_limit_high,
        )

        mean_for_mg = np.nan_to_num(np.mean([a.answer for a in answers]))

        result = compute_feedback_simple(mg_stat, mean_for_mg)
        milestone_group_results[milestonegroup.id] = result  # type: ignore
    return milestone_group_results


def compute_summary_milestonegroup_feedback_for_all_sessions(
    session: SessionDep,
    current_active_user: CurrentActiveUserDep,
    child_id: int,
    age_limit_low=6,
    age_limit_high=6,
) -> dict[str, dict[int, int]]:
    results: dict[str, dict[int, int]] = {}

    # get all answer sessions and filter for completed ones
    answersessions = [
        a
        for a in session.exec(
            select(MilestoneAnswerSession).where(
                col(MilestoneAnswerSession.child_id) == child_id
                and col(MilestoneAnswerSession.user_id) == current_active_user.id
            )
        ).all()
        if _session_has_expired(a)
    ]

    if answersessions == []:
        return results
    else:
        child = get_db_child(session, current_active_user, child_id)

        for answersession in answersessions:
            milestone_group_results = (
                compute_summary_milestonegroup_feedback_for_answersession(
                    session,
                    answersession,
                    child,
                    age_limit_low=age_limit_low,
                    age_limit_high=age_limit_high,
                )
            )

            datestring = answersession.created_at.strftime("%d-%m-%Y")
            results[datestring] = milestone_group_results

    return results


def compute_detailed_milestonegroup_feedback_for_all_sessions(
    session: SessionDep,
    current_active_user: CurrentActiveUserDep,
    child_id: int,
) -> dict[str, dict[int, dict[int, int]]]:
    results: dict[str, dict[int, dict[int, int]]] = {}

    # get all answer sessions and filter for completed ones
    answersessions = [
        a
        for a in session.exec(
            select(MilestoneAnswerSession).where(
                col(MilestoneAnswerSession.child_id) == child_id
                and col(MilestoneAnswerSession.user_id) == current_active_user.id
            )
        ).all()
        if _session_has_expired(a)
    ]

    if answersessions == []:
        return results
    else:
        child = get_db_child(session, current_active_user, child_id)

        for answersession in answersessions:
            milestone_group_results = (
                compute_detailed_milestonegroup_feedback_for_answersession(
                    session,
                    answersession,
                    child,
                )
            )

            datestring = answersession.created_at.strftime("%d-%m-%Y")
            results[datestring] = milestone_group_results

    return results
