import numpy as np
import pytest

from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.routers.scores import TrafficLight
from mondey_backend.routers.scores import compute_feedback_milestone_group
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


@pytest.mark.parametrize("n", [10, 100, 1000, 99999])
def test_compute_feedback_milestone_group(n: int):
    avg_scores = np.random.random_sample(n) * 3  # random scores between 0 and 3
    dummy_scores = MilestoneGroupAgeScore(
        milestone_group_id=1,
        age=8,
        count=len(avg_scores),
        sum_score=np.sum(avg_scores),
        sum_squaredscore=np.sum(np.square(avg_scores)),
    )
    mean = np.mean(avg_scores)
    stddev = np.std(avg_scores, ddof=1)

    assert dummy_scores.mean == pytest.approx(mean)
    assert dummy_scores.stddev == pytest.approx(stddev)

    # green
    assert compute_feedback_milestone_group(dummy_scores, mean) == 1
    assert compute_feedback_milestone_group(dummy_scores, mean + stddev) == 1
    assert compute_feedback_milestone_group(dummy_scores, mean - 0.99 * stddev) == 1

    # yellow
    assert compute_feedback_milestone_group(dummy_scores, mean - 1.01 * stddev) == 0
    assert compute_feedback_milestone_group(dummy_scores, mean - 1.99 * stddev) == 0

    # red
    assert compute_feedback_milestone_group(dummy_scores, mean - 2.01 * stddev) == -1
    assert compute_feedback_milestone_group(dummy_scores, mean - 2.99 * stddev) == -1
    assert compute_feedback_milestone_group(dummy_scores, mean - 3.01 * stddev) == -1


def test_compute_feedback_milestone_group_no_stats():
    assert compute_feedback_milestone_group(None, 1.0) == -2


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_compute_feedback_milestone_group_too_few_samples(n: int):
    dummy_scores = MilestoneGroupAgeScore(
        milestone_group_id=1,
        age=8,
        count=n,
        sum_score=1,
        sum_squaredscore=1,
    )
    assert compute_feedback_milestone_group(dummy_scores, 4) == -2
    assert compute_feedback_milestone_group(dummy_scores, 3) == -2
    assert compute_feedback_milestone_group(dummy_scores, 2) == -2
    assert compute_feedback_milestone_group(dummy_scores, 1) == -2
    assert compute_feedback_milestone_group(dummy_scores, 0) == -2


@pytest.mark.asyncio
async def test_compute_summary_milestonegroup_feedback_for_answersession_with_recompute(
    session, user_session
):
    child_age = 8
    existing_age_8_milestone_group1_scores = [np.mean([1, 0, 0])]  # existing statistics
    statistics = session.get(MilestoneGroupAgeScoreCollection, 1)
    assert statistics.scores[child_age].mean == pytest.approx(
        np.mean(existing_age_8_milestone_group1_scores)
    )
    assert (
        statistics.scores[child_age].stddev == 0
    )  # not enough samples to compute stddev
    # not enough stats to give feedback for answer session 1
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert feedback[1] == TrafficLight.invalid.value
    assert len(feedback) == 1
    # answer session 2
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 2)
    )
    assert feedback[1] == TrafficLight.invalid.value
    assert len(feedback) == 1

    # update stats to include answer sessions 2 and 4
    await async_update_stats(session, user_session)
    updated_age_8_milestone_group1_scores = (
        existing_age_8_milestone_group1_scores.copy()
    )
    updated_age_8_milestone_group1_scores.extend(
        [np.mean([1, 1, 0])]
    )  # answer session 2
    updated_age_8_milestone_group1_scores.extend(
        [np.mean([2, 0, 0])]
    )  # answer session 4
    statistics = session.get(MilestoneGroupAgeScoreCollection, 1)
    assert statistics.scores[child_age].mean == pytest.approx(
        np.mean(updated_age_8_milestone_group1_scores)
    )
    assert statistics.scores[child_age].stddev == pytest.approx(
        np.std(updated_age_8_milestone_group1_scores, ddof=1)
    )

    # still not enough stats to give feedback
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert feedback[1] == TrafficLight.invalid.value
    assert len(feedback) == 1
    feedback = compute_milestonegroup_feedback_summary(
        session, session.get(MilestoneAnswerSession, 2)
    )
    assert feedback[1] == TrafficLight.invalid.value
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
async def test_compute_detailed_milestonegroup_feedback_for_answersession(
    session, user_session
):
    feedback = compute_milestonegroup_feedback_detailed(
        session, session.get(MilestoneAnswerSession, 1)
    )
    assert len(feedback) == 1
    assert len(feedback[1]) == 2
    # milestone 1 expected age 6, child age 8, answer 1 -> yellow
    assert feedback[1][1] == TrafficLight.yellow.value
    # milestone 2 expected age 12, child age 8 -> green
    assert feedback[1][2] == TrafficLight.green.value
