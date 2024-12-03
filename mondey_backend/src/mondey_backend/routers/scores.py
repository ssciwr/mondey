from __future__ import annotations

from enum import Enum

import numpy as np

from ..models.milestones import MilestoneAgeScorePublic
from ..models.milestones import MilestoneGroupAgeScorePublic


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
    stat: MilestoneAgeScorePublic | MilestoneGroupAgeScorePublic,
    score: float,
    min_score: float | None = None,
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
        # TODO: Check again what client wants to happen in such cases?
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
