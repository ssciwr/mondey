import datetime

import numpy as np
import pandas as pd
import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import event

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.statistics import analyse_answer_session
from mondey_backend.statistics import async_update_stats
from mondey_backend.statistics import make_datatable


def test_rms_analysis_does_not_load_display_metadata(session):
    answer_session = session.get(MilestoneAnswerSession, 2)
    assert answer_session is not None
    session.expire_all()
    statements: list[str] = []

    def record_statement(_conn, _cursor, statement, _parameters, _context, _many):
        statements.append(statement.lower())

    engine = session.get_bind()
    event.listen(engine, "before_cursor_execute", record_statement)
    try:
        analysis = analyse_answer_session(session, answer_session)
    finally:
        event.remove(engine, "before_cursor_execute", record_statement)

    assert analysis.rms == pytest.approx(np.sqrt(0.5))
    assert analysis.answers == []
    assert not any("from milestone " in statement for statement in statements)
    assert not any("from milestonegroup" in statement for statement in statements)
    assert not any("from milestonetext" in statement for statement in statements)


@pytest.mark.parametrize("n", [2, 3, 10, 100, 1000, 99999])
def test_milestone_age_score(n: int):
    answers = np.random.randint(0, 4, size=n)
    score = MilestoneAgeScore(
        milestone_id=1,
        age=1,
        c0=np.sum(answers == 0),
        c1=np.sum(answers == 1),
        c2=np.sum(answers == 2),
        c3=np.sum(answers == 3),
    )
    assert score.count == n
    assert score.mean == pytest.approx(np.mean(answers))
    assert score.stddev == pytest.approx(np.std(answers, ddof=1))


def test_milestone_age_score_zero_samples():
    score = MilestoneAgeScore(milestone_id=1, age=1, c0=0, c1=0, c2=0, c3=0)
    assert score.count == 0
    assert score.mean == 0.0
    assert score.stddev == 0.0


def test_milestone_age_score_one_sample():
    score = MilestoneAgeScore(milestone_id=1, age=1, c0=0, c1=0, c2=0, c3=1)
    assert score.count == 1
    assert score.mean == 3.0
    assert score.stddev == 0.0


@pytest.mark.asyncio
async def test_calculate_milestone_statistics_by_age(session, user_session):
    m1 = session.get(MilestoneAgeScoreCollection, 1)
    m2 = session.get(MilestoneAgeScoreCollection, 2)

    # existing stats (only answer session 1)
    assert m1.milestone_id == 1
    assert m1.scores[8].count == 1
    assert np.isclose(m1.scores[8].mean, 1.0)
    assert np.isclose(m1.scores[8].stddev, 0.0)

    assert m2.milestone_id == 2
    assert m2.scores[8].count == 1
    assert np.isclose(m2.scores[8].mean, 0.0)
    assert np.isclose(m2.scores[8].stddev, 0.0)

    # updated stats (answer sessions 1, 2, 4)
    await async_update_stats(session, user_session)
    m1 = session.get(MilestoneAgeScoreCollection, 1)
    m2 = session.get(MilestoneAgeScoreCollection, 2)

    assert m1.milestone_id == 1
    # not enough answers to fit an age curve, so there is no automatic age estimate and
    # the ages set on the milestone itself are left to whatever an admin has set
    assert not m1.curve_fit_ok
    assert m1.scores[8].count == 3
    m1_scores = [1, 1, 2]
    assert m1.scores[8].mean == pytest.approx(np.mean(m1_scores))
    assert m1.scores[8].stddev == pytest.approx(np.std(m1_scores, ddof=1))

    assert m2.milestone_id == 2
    assert not m2.curve_fit_ok
    assert m2.scores[8].count == 3
    m2_scores = [0, 1, 0]
    assert m2.scores[8].mean == pytest.approx(np.mean(m2_scores))
    assert m2.scores[8].stddev == pytest.approx(np.std(m2_scores, ddof=1))


@pytest.mark.asyncio
async def test_calculate_milestonegroup_statistics(session, user_session):
    mg = session.get(MilestoneGroupAgeScoreCollection, 1)

    # existing stats (only answer session 1)
    answers = [np.mean([1, 0, 0])]
    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == len(answers)
    assert np.isclose(mg.scores[8].mean, np.mean(answers))
    # with only one answer, stddev is set to 0
    assert np.isclose(mg.scores[8].stddev, 0)

    # The test answer sessions only contain a handful of answers, all at a single child
    # age, so no milestone age curve can be fitted. Without a curve there is no value to
    # impute for a milestone that an answer session does not contain, so no milestone
    # contributes to the milestone group statistics and they are left empty.
    await async_update_stats(session, user_session)
    mg = session.get(MilestoneGroupAgeScoreCollection, 1)

    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == 0
    assert mg.scores[8].mean == 0
    assert mg.scores[8].stddev == 0


def test_analyse_answer_session_ignores_ages_with_no_answers(session):
    """
    A milestone that no child of this age has answered has no expected answer, so it must
    not contribute to the rms: counting it as an expected answer of 0 would make the first
    child of their age to achieve the milestone look suspicious.
    """
    # the test statistics only have an answer for milestone 1 at age 8, so at age 3 there
    # is nothing to compare against
    child = session.get(Child, 1)
    created_at = datetime.datetime(child.birth_year, child.birth_month, 1) + (
        relativedelta(months=3)
    )
    session.add(
        MilestoneAnswerSession(
            id=777,
            child_id=1,
            user_id=3,
            created_at=created_at,
            expired=True,
            completed=True,
            included_in_statistics=False,
            suspicious_state=SuspiciousState.unknown,
        )
    )
    session.add(
        MilestoneAnswer(
            answer_session_id=777, milestone_id=1, milestone_group_id=1, answer=3
        )
    )
    session.commit()

    analysis = analyse_answer_session(session, session.get(MilestoneAnswerSession, 777))

    assert analysis.child_age == 3
    assert analysis.answers == []
    assert analysis.rms == 0.0


@pytest.mark.asyncio
async def test_calculate_statistics_with_empty_milestone_group(session, user_session):
    # a milestone group with no milestones must not break the statistics update:
    # previously the group's average score was computed as 0/0 = nan, which then
    # failed to be written to the database
    session.add(MilestoneGroup(id=99, order=99))
    session.commit()

    result = await async_update_stats(session, user_session)
    assert result.answer_sessions > 0

    mg = session.get(MilestoneGroupAgeScoreCollection, 99)
    assert mg is not None
    for score in mg.scores:
        assert score.count == 0
        assert not np.isnan(score.sum_score)
        assert not np.isnan(score.sum_squaredscore)
        assert score.sum_score == 0.0
        assert score.sum_squaredscore == 0.0


def test_make_datatable_no_data():
    df = make_datatable(
        [], pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), {}, {}
    )
    assert df.shape == (0, 0)


def test_make_datatable_includes_research_group_id():
    answer_session = MilestoneAnswerSession(
        id=42,
        child_id=2,
        user_id=3,
        expired=False,
        completed=True,
        included_in_statistics=True,
    )

    df = make_datatable(
        [answer_session],
        pd.DataFrame([]),
        pd.DataFrame([]),
        pd.DataFrame([]),
        {42: 12},
        {3: 123451},
    )

    assert df.loc[42, "research_group_id"] == 123451
