from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.routers.scores import compute_feedback_for_milestonegroup
from mondey_backend.routers.scores import compute_feedback_simple


def test_compute_feedback_simple():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1, age_months=8, avg_score=2.0, sigma_score=0.8, expected_score=1.0
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_compute_feedback_simple_bad_data():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1, age_months=8, avg_score=2.0, sigma_score=0, expected_score=1.0
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1

    dummy_scores.avg_score = 0
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == 1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 1

    score = 2
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_compute_feedback_for_milestonegroup(session):
    answersession = session.exec(select(MilestoneAnswerSession)).first()

    total, detailed = compute_feedback_for_milestonegroup(
        session,
        1,
        answersession,
        8,
        age_limit_low=6,
        age_limit_high=6,
        with_detailed=True,
    )
    assert total == 0
    assert detailed == {1: 0, 2: 0}

    total, detailed = compute_feedback_for_milestonegroup(
        session,
        1,
        answersession,
        8,
        age_limit_low=6,
        age_limit_high=6,
        with_detailed=False,
    )

    assert total == 0
    assert detailed is None


def test_compute_feedback_for_milestonegroup_bad_data(session):
    answersession = session.exec(select(MilestoneAnswerSession)).first()
    answersession.answers = {}
    total, detailed = compute_feedback_for_milestonegroup(
        session,
        1,
        answersession,
        8,
        age_limit_low=6,
        age_limit_high=6,
        with_detailed=True,
    )
    assert total == -2
    assert detailed is None
