from __future__ import annotations

from enum import Enum

import numpy as np

from ..dependencies import SessionDep
from ..models.milestones import MilestoneAgeScore
from ..models.milestones import MilestoneAnswerSession
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAgeScore
from .utils import calculate_milestone_age_scores
from .utils import calculate_milestone_group_age_scores
from .utils import get


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
    stat: MilestoneAgeScore | MilestoneGroupAgeScore, score: float
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


def compute_feedback_for_milestonegroup(
    session: SessionDep,
    milestonegroup_id: int,
    answer_session: MilestoneAnswerSession,
    age: int,
    age_limit_low: int = 6,
    age_limit_high: int = 6,
    with_detailed: bool = False,
    mg_score=None,
) -> tuple[int, dict[int, int]] | tuple[int, None]:
    """
    Compute trafficlight feedback for milestonegroup.

    Parameters
    ----------
    session : SessionDep
        Current database session
    milestonegroup_id : int
        Relevant milestone group to compute the feedback for
    answer_session : MilestoneAnswerSession
        Current answer session. Child's score that is to be evaluated is derived from this as mean(answers)
    age : int
        child age
    age_limit_low : int, optional
        number of months subtracted from age to get lower limit for relevant milestones. Lower limit will be age - age_limit_low, by default 6
    age_limit_high : int, optional
        number of months added to age to get upper limit for relevant milestones. Upper limit will be age - age_limit_upper,, by default 6
    with_detailed : bool, optional
        Whether a detailed feedback for each milestone at the current age is desired or not, by default False
    mg_score : _type_, optional
        Statistics over the milestonegroup for the age interval [age-age_limit_low, age+age_limit_high). Will be computed if None. by default None

    Returns
    -------
    int | tuple[int, dict[int, int]]
        the trafficlight feedback for the milestone group.
        -1 if child score <= group_avg - 2 * group_stddev (trafficlight: red)
        0 if group_avg - 2 * group_stddev < score <= group_avg - group_stddev (trafficlight: yellow)
        1 if score > group_avg - group_stddev (trafficlight: green)

        If with_detailed is True, a tuple is returned with the first element being the total feedback and the second element being a dictionary with the feedback for each milestone in the milestonegroup.
    """
    age_lower = age - age_limit_low
    age_upper = age + age_limit_high
    milestonegroup = get(session, MilestoneGroup, milestonegroup_id)

    # get the relevant answers for the child
    answers = {
        k: v
        for k, v in answer_session.answers.items()
        if k in [m.id for m in milestonegroup.milestones]
    }

    if answers == {}:
        return TrafficLight.invalid.value, None

    # compute value for child
    mean_score_child = np.nan_to_num(np.mean([a.answer for a in answers.values()]))

    # compute milestone group statistics over relevant age range.
    # this gets all answers that exist for the milestones in the group
    if mg_score is None:
        mg_score = calculate_milestone_group_age_scores(
            session,
            milestonegroup,  # type: ignore
            age,
            age_lower=age_lower,
            age_upper=age_upper,
        )
    # compute feedback for the milestonegroup as a whole.
    total_feedback = compute_feedback_simple(
        mg_score,
        mean_score_child,
    )

    if with_detailed:
        # compute individual feedback for each milestone for the current time point
        detailed_feedback: dict[int, int] = {}

        for milestone_id, answer in answers.items():
            statistics = calculate_milestone_age_scores(session, milestone_id)  # type: ignore

            feedback = compute_feedback_simple(
                statistics.scores[age],
                answer.answer,  # type: ignore
            )
            detailed_feedback[milestone_id] = feedback  # type: ignore

        return total_feedback, detailed_feedback
    else:
        return total_feedback, None
