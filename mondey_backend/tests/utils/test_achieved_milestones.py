import datetime

from sqlalchemy import event

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.routers.utils import get_previously_achieved_milestone_ids
from mondey_backend.routers.utils import (
    iter_sessions_with_previously_achieved_milestone_ids,
)


def make_session(
    session,
    session_id: int,
    child_id: int,
    day: int,
    answers: dict[int, int],
    *,
    completed: bool = True,
    suspicious_state: SuspiciousState = SuspiciousState.not_suspicious,
) -> None:
    session.add(
        MilestoneAnswerSession(
            id=session_id,
            child_id=child_id,
            user_id=3,
            created_at=datetime.datetime(2025, 1, day),
            expired=True,
            completed=completed,
            included_in_statistics=False,
            suspicious_state=suspicious_state,
        )
    )
    for milestone_id, answer in answers.items():
        session.add(
            MilestoneAnswer(
                answer_session_id=session_id,
                milestone_id=milestone_id,
                milestone_group_id=1,
                answer=answer,
            )
        )
    session.commit()


def prior_achievements_by_session(session, *session_ids: int) -> dict[int, set[int]]:
    answer_sessions = []
    for session_id in session_ids:
        answer_session = session.get(MilestoneAnswerSession, session_id)
        assert answer_session is not None
        answer_sessions.append(answer_session)

    result: dict[int, set[int]] = {}
    for (
        answer_session,
        achieved_milestone_ids,
    ) in iter_sessions_with_previously_achieved_milestone_ids(session, answer_sessions):
        answer_session_id = answer_session.id
        assert answer_session_id is not None
        result[answer_session_id] = set(achieved_milestone_ids)
    return result


def test_achieved_milestones_are_those_answered_3_earlier(session):
    # milestone 1 achieved, milestone 2 not
    make_session(session, 101, 10, day=1, answers={1: 3, 2: 1})
    achieved = get_previously_achieved_milestone_ids(
        session, 10, datetime.datetime(2025, 1, 15)
    )
    assert achieved == {1}


def test_achieved_milestones_only_counts_earlier_sessions(session):
    """
    A milestone achieved *later* must not be treated as achieved for an earlier session:
    it was missing from that session because the child was too young, not because they
    had already achieved it.
    """
    make_session(session, 102, 11, day=20, answers={1: 3})
    # as of day 10, the child has not achieved anything yet
    assert (
        get_previously_achieved_milestone_ids(
            session, 11, datetime.datetime(2025, 1, 10)
        )
        == set()
    )
    # as of day 25 they have
    assert get_previously_achieved_milestone_ids(
        session, 11, datetime.datetime(2025, 1, 25)
    ) == {1}


def test_achieved_milestones_are_per_child(session):
    make_session(session, 103, 12, day=1, answers={1: 3})
    assert (
        get_previously_achieved_milestone_ids(
            session, 13, datetime.datetime(2025, 1, 15)
        )
        == set()
    )


def test_achieved_milestones_ignores_incomplete_sessions(session):
    """An incomplete session is not used to stop asking about a milestone."""
    session.add(
        MilestoneAnswerSession(
            id=104,
            child_id=14,
            user_id=3,
            created_at=datetime.datetime(2025, 1, 1),
            expired=False,
            completed=False,
            included_in_statistics=False,
            suspicious_state=SuspiciousState.unknown,
        )
    )
    session.add(
        MilestoneAnswer(
            answer_session_id=104, milestone_id=1, milestone_group_id=1, answer=3
        )
    )
    session.commit()
    assert (
        get_previously_achieved_milestone_ids(
            session, 14, datetime.datetime(2025, 1, 15)
        )
        == set()
    )


def test_iter_sessions_carries_forward_only_earlier_achievements(session):
    make_session(session, 201, 20, day=1, answers={1: 2, 2: 3})
    make_session(session, 202, 20, day=2, answers={})
    make_session(session, 203, 20, day=3, answers={1: 3})
    make_session(session, 204, 20, day=4, answers={})

    # Supply the target sessions out of order: the iterator is responsible for
    # processing them chronologically.
    achieved = prior_achievements_by_session(session, 204, 202)

    assert achieved[202] == {2}
    assert achieved[204] == {1, 2}


def test_iter_sessions_includes_excluded_sessions_but_not_same_time(session):
    make_session(
        session,
        211,
        21,
        day=1,
        answers={1: 3},
        suspicious_state=SuspiciousState.suspicious,
    )
    make_session(session, 212, 21, day=2, answers={})
    make_session(
        session,
        213,
        21,
        day=2,
        answers={2: 3},
        suspicious_state=SuspiciousState.suspicious,
    )
    make_session(session, 214, 21, day=2, answers={})
    make_session(session, 215, 21, day=3, answers={})

    achieved = prior_achievements_by_session(session, 215, 214, 212)

    # Suspicious sessions are excluded from statistics, but an achievement in one still
    # explains why the milestone is absent from a later questionnaire.
    assert achieved[212] == {1}
    assert achieved[214] == {1}
    assert achieved[215] == {1, 2}


def test_iter_sessions_ignores_achievements_from_incomplete_sessions(session):
    make_session(session, 221, 22, day=1, answers={1: 3}, completed=False)
    make_session(session, 222, 22, day=2, answers={})

    assert prior_achievements_by_session(session, 222)[222] == set()


def test_iter_sessions_reads_achievement_history_with_one_query(session):
    for day in range(1, 6):
        make_session(session, 230 + day, 23, day=day, answers={day: 3})
    answer_sessions = [
        session.get(MilestoneAnswerSession, session_id)
        for session_id in (232, 233, 234, 235)
    ]
    assert all(answer_session is not None for answer_session in answer_sessions)

    select_statements: list[str] = []

    def record_statement(_conn, _cursor, statement, _params, _context, _many):
        if statement.lstrip().upper().startswith("SELECT"):
            select_statements.append(statement)

    engine = session.get_bind()
    event.listen(engine, "before_cursor_execute", record_statement)
    try:
        snapshots = [
            set(achieved_milestone_ids)
            for _, achieved_milestone_ids in (
                iter_sessions_with_previously_achieved_milestone_ids(
                    session, answer_sessions
                )
            )
        ]
    finally:
        event.remove(engine, "before_cursor_execute", record_statement)

    assert snapshots == [{1}, {1, 2}, {1, 2, 3}, {1, 2, 3, 4}]
    assert len(select_statements) == 1
