import pytest
from fastapi import HTTPException
from sqlmodel import select

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.utils import count_milestone_answers_for_milestone
from mondey_backend.routers.utils import get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import get_db_milestone_answer_session
from mondey_backend.routers.utils import get_milestonegroups_for_answersession
from mondey_backend.routers.utils import get_or_create_current_milestone_answer_session


def test_create_answer_session_requires_persisted_child(session, active_user):
    child = Child(birth_year=2025, birth_month=1, user_id=3, has_image=False)
    with pytest.raises(ValueError, match="Child must have an ID"):
        get_or_create_current_milestone_answer_session(session, active_user, child)


def test_create_answer_session_rejects_milestone_without_group(session, active_user):
    milestone = session.get(Milestone, 3)
    milestone.group_id = None
    child = session.get(Child, 2)
    with pytest.raises(ValueError, match="Milestone 3 has no group ID"):
        get_or_create_current_milestone_answer_session(session, active_user, child)


def test_create_answer_session_rejects_previous_milestone_without_group(
    session, active_user
):
    milestone = session.get(Milestone, 1)
    milestone.group_id = None
    milestone.relevant_age_max = 0
    child = session.get(Child, 1)
    with pytest.raises(ValueError, match="Milestone 1 has no group ID"):
        get_or_create_current_milestone_answer_session(session, active_user, child)


def test_get_milestonegroups_for_answersession(session):
    answersession = session.get(MilestoneAnswerSession, 1)
    milestonegroups = get_milestonegroups_for_answersession(session, answersession)

    assert milestonegroups[1].id == 1
    assert len(milestonegroups) == 1

    answersession = session.get(MilestoneAnswerSession, 2)
    milestonegroups = session.exec(select(MilestoneGroup)).all()

    milestonegroups = get_milestonegroups_for_answersession(session, answersession)
    assert len(milestonegroups) == 1
    assert milestonegroups[1].id == 1


def test_get_answer_session_child_ages_in_months(session):
    answer_sessions = session.exec(select(MilestoneAnswerSession)).all()
    child_ages = get_answer_session_child_ages_in_months(session, answer_sessions)

    assert len(child_ages) == 7
    assert child_ages[1] == 8
    assert child_ages[2] == 8
    assert child_ages[3] == 55
    assert child_ages[4] == 8
    assert child_ages[5] == 43
    assert child_ages[6] == 55
    assert child_ages[99] == 8


def test_count_milestone_answers(session):
    result = count_milestone_answers_for_milestone(session, milestone_id=2)
    assert type(result) is int
    assert result == 4


def test_count_milestone_answers_non_existing(session):
    result = count_milestone_answers_for_milestone(session, milestone_id=9999954)
    assert type(result) is int
    assert result == 0


def test_get_db_milestone_answer_session_allows_owner(session, active_user):
    answer_session = get_db_milestone_answer_session(session, active_user, 1)
    assert answer_session.id == 1


def test_get_db_milestone_answer_session_rejects_non_owner(
    session, active_research_user
):
    with pytest.raises(HTTPException) as exc_info:
        get_db_milestone_answer_session(session, active_research_user, 1)
    assert exc_info.value.status_code == 404


def test_get_db_milestone_answer_session_allows_admin(session, active_admin_user):
    answer_session = get_db_milestone_answer_session(session, active_admin_user, 1)
    assert answer_session.id == 1
