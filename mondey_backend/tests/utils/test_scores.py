import numpy as np
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
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


@pytest.mark.asyncio
async def test_compute_summary_milestonegroup_feedback_for_answersession_with_recompute(
    session, user_session
):
    child_age = 8
    existing_age_8_milestone_group1_scores = [1, 0, 0]  # existing statistics
    statistics = session.exec(
        select(MilestoneGroupAgeScoreCollection).where(
            MilestoneGroupAgeScoreCollection.milestone_group_id == 1
        )
    ).all()
    assert len(statistics) == 1
    assert statistics[0].scores[child_age].avg_score == pytest.approx(
        np.mean(existing_age_8_milestone_group1_scores), abs=0.001
    )
    assert statistics[0].scores[child_age].stddev_score == pytest.approx(
        np.std(existing_age_8_milestone_group1_scores), abs=0.001
    )
    # answer session 1 scores for milestone group 1: [1, 0, 0] -> mean 0.33 -> green
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert feedback[1] == TrafficLight.green.value
    assert len(feedback) == 1
    # answer session 2 scores for milestone group 1: [1, 1, 0] -> mean 0.66 -> green
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 2)
    )
    assert feedback[1] == TrafficLight.green.value
    assert len(feedback) == 1
    for incremental_update in [True, False]:
        await async_update_stats(
            session,
            user_session,
            incremental_update=incremental_update,
        )
        updated_age_8_milestone_group1_scores = (
            existing_age_8_milestone_group1_scores.copy()
        )
        updated_age_8_milestone_group1_scores.extend([1, 1, 0])  # answer session 2
        updated_age_8_milestone_group1_scores.extend([2, 0, 0])  # answer session 4
        statistics = session.get(MilestoneGroupAgeScoreCollection, 1)
        assert statistics.scores[child_age].avg_score == pytest.approx(
            np.mean(updated_age_8_milestone_group1_scores), abs=0.001
        )
        assert statistics.scores[child_age].stddev_score == pytest.approx(
            np.std(updated_age_8_milestone_group1_scores), abs=0.1
        )
        # answer session 1 score 0.5 -> remains green
        feedback = compute_milestonegroup_feedback_summary(
            session, session.get(MilestoneAnswerSession, 1)
        )
        assert feedback[1] == TrafficLight.green.value
        assert len(feedback) == 1
        # answer session 2 score 1.5 -> remains green
        feedback = compute_milestonegroup_feedback_summary(
            session, session.get(MilestoneAnswerSession, 2)
        )
        assert feedback[1] == TrafficLight.green.value
        assert len(feedback) == 1


def test_compute_summary_milestonegroup_feedback_for_answersession_no_existing_stat(
    session,
):
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 3)
    )

    assert len(feedback) == 1
    assert feedback[2] == TrafficLight.invalid.value


@pytest.mark.asyncio
async def test_compute_detailed_milestonegroup_feedback_for_answersession_with_recompute(
    session, user_session
):
    # initial stats only include answer session 1: all feedback green
    feedback = compute_milestonegroup_feedback_detailed(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    assert feedback[1][1] == TrafficLight.green.value
    assert feedback[1][2] == TrafficLight.green.value

    # updated stats include more answer sessions
    await async_update_stats(session, user_session, incremental_update=True)
    feedback = compute_milestonegroup_feedback_detailed(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    assert feedback[1][1] == TrafficLight.green.value
    assert feedback[1][2] == TrafficLight.green.value


def test_compute_detailed_milestonegroup_feedback_for_answersession_no_existing_stat(
    session,
):
    feedback = compute_milestonegroup_feedback_detailed(
        session, session.get(MilestoneAnswerSession, 3)
    )
    assert len(feedback) == 1
    assert feedback[2][5] == TrafficLight.invalid.value
