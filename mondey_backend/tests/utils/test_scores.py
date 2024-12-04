from datetime import datetime
from datetime import timedelta

from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
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


def test_compute_summary_milestonegroup_feedback_for_answersession(session):
    feedback = compute_milestonegroup_feedback_summary(
        session, child_id=1, answersession_id=1
    )

    # the statistics for the given answersession specify mean = 2.3, stddev = 0.45 for ages 8, 9
    # where we have answers for milestone 1 (age 8) and milestone 2 (age 9)
    # with the child being age 8, we only have milestonegroup 1 with milestone 1 and 2, which yields
    # avg 1.5, min = 1 ==> yellowWithCaveat
    assert feedback[1] == TrafficLight.yellowWithCaveat.value
    assert len(feedback) == 1

    # same as above, but for answers 4, 3  -> 3.5 ==> green
    feedback = compute_milestonegroup_feedback_summary(
        session, child_id=1, answersession_id=2
    )
    assert len(feedback) == 1
    assert feedback[1] == TrafficLight.green.value


def test_compute_summary_milestonegroup_feedback_for_answersession_recompute_statistics(
    session,
):
    feedback = compute_milestonegroup_feedback_summary(
        session, child_id=3, answersession_id=3
    )

    # child is 42 months old, for which there is no data. Hence the feedback is invalid
    assert len(feedback) == 1
    assert feedback[2] == TrafficLight.invalid.value

    # check that the statistics have been updated
    statistics = session.exec(
        select(MilestoneGroupAgeScoreCollection).where(
            MilestoneGroupAgeScoreCollection.milestone_group_id == 2
        )
    ).all()
    assert len(statistics) == 1
    assert statistics[0].created_at >= datetime.now() - timedelta(
        minutes=3
    )  # can be at max 3 min old

    for i, score in enumerate(statistics[0].scores):
        if i in [8, 9]:
            assert score.avg_score > 0
            assert score.stddev_score > 0
            assert score.count == 2

        if i == 65:
            assert score.avg_score > 0
            assert score.stddev_score == 0
            assert score.count == 1

        if i not in [8, 9, 65]:
            assert score.avg_score == 0
            assert score.stddev_score == 0
            assert score.count == 0


def test_compute_detailed_milestonegroup_feedback_for_answersession(session):
    # with the child being age 8, we only have milestonegroup 1 with milestone 1 and 2 for answersession 1, which yields
    # answers 1, 2 compared to mean = 1.5, stddev = 0.702
    feedback = compute_milestonegroup_feedback_detailed(
        session, child_id=1, answersession_id=1
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    assert feedback[1][1] == TrafficLight.green.value
    assert feedback[1][2] == TrafficLight.green.value


def test_compute_detailed_milestonegroup_feedback_for_answersession_recompute_statistics(
    session,
):
    feedback = compute_milestonegroup_feedback_detailed(
        session, child_id=3, answersession_id=3
    )

    assert len(feedback) == 1
    assert len(feedback[2]) == 1
    assert (
        feedback[2][7] == TrafficLight.invalid.value
    )  # for the respective age we have no data

    # check that the statistics have been updated
    statistics = session.exec(
        select(MilestoneAgeScoreCollection).where(
            MilestoneAgeScoreCollection.milestone_id == 7
        )
    ).all()
    assert len(statistics) == 1
    assert statistics[0].created_at >= datetime.now() - timedelta(
        minutes=3
    )  # can be at max 3 min old

    for i, score in enumerate(statistics[0].scores):
        if i in [8, 9]:
            assert score.avg_score > 0
            assert score.stddev_score > 0
            assert score.count == 2

        if i == 65:
            assert score.avg_score > 0
            assert score.stddev_score == 0
            assert score.count == 1

        if i not in [8, 9, 65]:
            assert score.avg_score == 0
            assert score.stddev_score == 0
            assert score.count == 0
