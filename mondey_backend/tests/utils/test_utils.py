from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import get_milestonegroups_for_answersession


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
    child_ages = _get_answer_session_child_ages_in_months(session, answer_sessions)

    assert len(child_ages) == 3
    assert child_ages[1] == 8
    assert child_ages[2] == 8
    assert child_ages[3] == 55
