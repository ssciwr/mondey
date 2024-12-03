from sqlmodel import select

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.routers.scores import (
    compute_detailed_milestonegroup_feedback_for_answersession,
)
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.scores import (
    compute_summary_milestonegroup_feedback_for_answersession,
)
from mondey_backend.routers.scores import get_milestonegroups_for_answersession


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


def test_compute_detailed_milestonegroup_feedback_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)

    child = session.exec(select(Child).where(Child.user_id == 1)).first()
    result = compute_detailed_milestonegroup_feedback_for_answersession(
        session, answersession, child
    )

    assert result == {1: {1: 2, 2: 2}}


def test_compute_detailed_milestonegroup_feedback_for_answersession_no_data(session):
    answersession = session.get(MilestoneAnswerSession, 3)
    child = session.exec(select(Child).where(Child.user_id == 3)).first()
    result = compute_detailed_milestonegroup_feedback_for_answersession(
        session, answersession, child
    )
    assert result == {}


def test_compute_summary_milestonegroup_feedback_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)
    child = session.exec(select(Child).where(Child.user_id == 3)).first()

    result = compute_summary_milestonegroup_feedback_for_answersession(
        session, answersession, child, age_limit_low=6, age_limit_high=6
    )
    assert result == {1: 0}


def test_compute_summary_milestonegroup_feedback_for_answersession_no_data(session):
    answersession = session.get(MilestoneAnswerSession, 3)
    child = session.exec(select(Child).where(Child.user_id == 3)).first()

    result = compute_summary_milestonegroup_feedback_for_answersession(
        session, answersession, child, age_limit_low=6, age_limit_high=6
    )

    assert result == {}
