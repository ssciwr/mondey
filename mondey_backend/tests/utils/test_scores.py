import pytest
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.routers.scores import TrafficLight
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.scores import compute_milestonegroup_feedback_detailed
from mondey_backend.routers.scores import compute_milestonegroup_feedback_summary
from mondey_backend.routers.utils import get_milestonegroups_for_answersession
from mondey_backend.statistics import async_update_stats


def test_get_milestonegroups_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)
    milestonegroups = get_milestonegroups_for_answersession(session, answersession)
    assert len(milestonegroups) == 1
    assert milestonegroups[1].id == 1


def test_get_milestonegroups_for_answersession_no_data(session):
    milestonegroups = get_milestonegroups_for_answersession(
        session, MilestoneAnswerSession()
    )
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
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


@pytest.mark.asyncio
async def test_compute_summary_milestonegroup_feedback_for_answersession_with_recompute(
    statistics_session, user_session
):
    child_age = 8
    # existing statistics for milestonegroup 1 at age 8 months: [0,1] -> mean = 0.5 +/- 0.5
    statistics = statistics_session.exec(
        select(MilestoneGroupAgeScoreCollection).where(
            MilestoneGroupAgeScoreCollection.milestone_group_id == 1
        )
    ).all()
    assert len(statistics) == 1
    assert statistics[0].scores[child_age].avg_score == pytest.approx(0.5, abs=0.001)
    assert statistics[0].scores[child_age].stddev_score == pytest.approx(0.5, abs=0.001)
    # answer session 1 scores: [0, 1] -> mean 0.5 -> green
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=1, answersession_id=1
    )
    assert feedback[1] == TrafficLight.green.value
    assert len(feedback) == 1
    # answer session 2 scores: [2, 3] -> mean 2.5 -> green
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=1, answersession_id=2
    )
    assert feedback[1] == TrafficLight.green.value
    assert len(feedback) == 1
    for update_existing_statistics in [True, False]:
        await async_update_stats(
            statistics_session,
            user_session,
            incremental_update=update_existing_statistics,
        )
        # updated stats for milestonegroup 1 at age 8 months: [0,1,2,3,2,3] -> mean = 1.83333 +/- ~1.2
        statistics = statistics_session.exec(
            select(MilestoneGroupAgeScoreCollection).where(
                MilestoneGroupAgeScoreCollection.milestone_group_id == 1
            )
        ).all()
        assert len(statistics) == 1
        assert statistics[0].scores[child_age].avg_score == pytest.approx(
            1.83333, abs=0.001
        )
        assert statistics[0].scores[child_age].stddev_score == pytest.approx(
            1.2, abs=0.1
        )
        # answer session 1 score 0.5 -> yellow
        feedback = compute_milestonegroup_feedback_summary(
            statistics_session, child_id=1, answersession_id=1
        )
        assert feedback[1] == TrafficLight.yellow.value
        assert len(feedback) == 1
        # answer session 2 score 2.5 remain green
        feedback = compute_milestonegroup_feedback_summary(
            statistics_session, child_id=1, answersession_id=2
        )
        assert feedback[1] == TrafficLight.green.value
        assert len(feedback) == 1


def test_compute_summary_milestonegroup_feedback_for_answersession_no_existing_stat(
    statistics_session,
):
    feedback = compute_milestonegroup_feedback_summary(
        statistics_session, child_id=3, answersession_id=3
    )

    assert len(feedback) == 1
    assert feedback[2] == TrafficLight.invalid.value


@pytest.mark.asyncio
async def test_compute_detailed_milestonegroup_feedback_for_answersession_with_recompute(
    statistics_session, user_session
):
    # initial stats only include answer session 1: all feedback green
    feedback = compute_milestonegroup_feedback_detailed(
        statistics_session, child_id=1, answersession_id=1
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    assert feedback[1][1] == TrafficLight.green.value
    assert feedback[1][2] == TrafficLight.green.value

    # updated stats include more answer sessions
    await async_update_stats(statistics_session, user_session, incremental_update=True)
    feedback = compute_milestonegroup_feedback_detailed(
        statistics_session, child_id=1, answersession_id=1
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    # milestone 1: score 2, mean = 2.33+/-1.2 -> yellow
    assert feedback[1][1] == TrafficLight.yellow.value
    # milestone 2: score 1, mean = 1.33+/-1.2 -> yellow
    assert feedback[1][2] == TrafficLight.yellow.value


def test_compute_detailed_milestonegroup_feedback_for_answersession_no_existing_stat(
    statistics_session,
):
    feedback = compute_milestonegroup_feedback_detailed(
        statistics_session, child_id=3, answersession_id=3
    )
    assert len(feedback) == 1
    assert feedback[2][5] == TrafficLight.invalid.value
