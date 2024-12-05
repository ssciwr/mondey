from datetime import datetime
from datetime import timedelta

import numpy as np
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.routers.scores import TrafficLight
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.scores import compute_milestonegroup_feedback_detailed
from mondey_backend.routers.scores import compute_milestonegroup_feedback_summary
from mondey_backend.routers.utils import get_milestonegroups_for_answersession


def test_get_milestonegroups_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)
    milestonegroups = get_milestonegroups_for_answersession(session, answersession)
    assert len(milestonegroups) == 1
    assert milestonegroups[1].id == 1


def test_get_milestonegroups_for_answersession_no_data(session):
    answersession = session.get(MilestoneAnswerSession, 3)
    milestonegroups = get_milestonegroups_for_answersession(session, answersession)
    assert len(milestonegroups) == 0


def test_compute_feedback_simple():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1,
        age_months=8,
        avg_score=2.0,
        stddev_score=0.8,
        expected_score=1.0,
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -2

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 2

    dummy_scores = MilestoneGroupAgeScore(
        milestonegroup_id=1,
        age_months=8,
        avg_score=3.0,
        stddev_score=1.2,
    )


def test_compute_summary_milestonegroup_feedback_for_answersession_with_recompute(
    statistics_session,
):
    # there is an existing statistics for milestonegroup 1, which has milestones 1 and 2
    # which gives mean = 1.92 and stddev = 0.21, and we have 2 additional answers for these m
    # milestones with answers 3 and 2 for milestones 1 and 2 respectively. ==> statistics
    # changes to mean = 2.446 +/- 0.89. The first call updates the statistics with the new
    # values, the second does not.
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=1, answersession_id=1
    )

    assert feedback[1] == TrafficLight.yellow.value
    assert len(feedback) == 1

    # same as above, but for answers 4, 3  -> 3.5 ==> green
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=1, answersession_id=2
    )
    assert len(feedback) == 1
    assert feedback[1] == TrafficLight.green.value


def test_compute_summary_milestonegroup_feedback_for_answersession_no_existing_stat(
    statistics_session,
):
    # there is only 2 answer sfor milestonegroup 2 which only has milestone 7.
    # these 2 are from 2 answersessions which are 10 days apart so fall into the
    # same age group => the feedback has only one entry for milestonegroup 2
    # and because the answers are 3 and 2 -> avg = 2.5 +/- 0.7071 -> green for answer = 3
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=3, answersession_id=3
    )

    assert len(feedback) == 1
    assert feedback[2] == TrafficLight.green.value

    #  check that the statistics have been updated
    statistics = statistics_session.exec(
        select(MilestoneGroupAgeScoreCollection).where(
            MilestoneGroupAgeScoreCollection.milestone_group_id == 2
        )
    ).all()
    assert len(statistics) == 1
    assert statistics[0].created_at >= datetime.now() - timedelta(
        minutes=1
    )  # can be at max 1 min old

    assert statistics[0].scores[42].count == 2
    assert np.isclose(statistics[0].scores[42].avg_score, 2.5)
    assert np.isclose(statistics[0].scores[42].stddev_score, 0.7071)

    for i, score in enumerate(statistics[0].scores):
        if i != 42:
            assert np.isclose(score.avg_score, 0)
            assert np.isclose(score.stddev_score, 0)
            assert np.isclose(score.count, 0)


def test_compute_detailed_milestonegroup_feedback_for_answersession_with_recompute(
    statistics_session,
):
    feedback = compute_milestonegroup_feedback_detailed(
        statistics_session, child_id=1, answersession_id=1
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    assert feedback[1][1] == TrafficLight.green.red.value
    assert feedback[1][2] == TrafficLight.green.red.value


def test_compute_detailed_milestonegroup_feedback_for_answersession_no_stat(
    statistics_session,
):
    # follows the same logic as the corresponding test for the milestonegroup summary feedback
    feedback = compute_milestonegroup_feedback_detailed(
        statistics_session, child_id=3, answersession_id=3
    )

    assert len(feedback) == 1
    assert feedback[2][7] == TrafficLight.green.green.value
