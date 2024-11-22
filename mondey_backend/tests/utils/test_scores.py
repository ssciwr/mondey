from sqlmodel import select

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.routers.scores import (
    compute_detailed_milestonegroup_feedback_for_all_sessions,
)
from mondey_backend.routers.scores import (
    compute_detailed_milestonegroup_feedback_for_answersession,
)
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.scores import (
    compute_summary_milestonegroup_feedback_for_all_sessions,
)
from mondey_backend.routers.scores import (
    compute_summary_milestonegroup_feedback_for_answersession,
)
from mondey_backend.routers.scores import get_milestonegroups_for_answersession
from mondey_backend.routers.utils import _session_has_expired
from mondey_backend.users import fastapi_users


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
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_compute_detailed_milestonegroup_feedback_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)

    child = session.exec(select(Child).where(Child.user_id == 1)).first()
    result = compute_detailed_milestonegroup_feedback_for_answersession(
        session, answersession, child
    )

    assert result == {1: {1: 1, 2: 1}}  # FIXME: check this again


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


def test_compute_summary_milestonegroup_feedback_for_all_sessions(session):
    child = session.exec(select(Child).where(Child.user_id == 3)).first()
    user = fastapi_users.current_user(active=True)
    result = compute_summary_milestonegroup_feedback_for_all_sessions(
        session, user, child, age_limit_low=6, age_limit_high=6
    )

    relevant_answersession = list(
        filter(
            lambda a: _session_has_expired(a),
            session.exec(
                select(MilestoneAnswerSession).where(
                    MilestoneAnswerSession.child_id == child.id
                    and MilestoneAnswerSession.user_id == user.id
                )
            ).all(),
        )
    )
    expected_result = {
        answersession.created_at.strftime("%d-%m-%Y"): {1: 0}
        for answersession in relevant_answersession
    }
    assert len(result) == len(relevant_answersession)

    assert result == expected_result


def test_compute_detailed_milestonegroup_feedback_for_all_sessions(session):
    child = session.exec(select(Child).where(Child.user_id == 3)).first()
    user = fastapi_users.current_user(active=True)

    result = compute_detailed_milestonegroup_feedback_for_all_sessions(
        session, user, child
    )
    relevant_answersession = list(
        filter(
            lambda a: _session_has_expired(a),
            session.exec(
                select(MilestoneAnswerSession).where(
                    MilestoneAnswerSession.child_id == child.id
                    and MilestoneAnswerSession.user_id == user.id
                )
            ).all(),
        )
    )
    expected_result = {
        answersession.created_at.strftime("%d-%m-%Y"): {1: {1: 0, 2: 0}}
        for answersession in relevant_answersession
    }
    assert len(result) == len(relevant_answersession)
    assert result == expected_result
