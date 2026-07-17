import numpy as np
import pandas as pd
import pytest
from sqlalchemy import event

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
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
    assert m1.expected_age == 8
    assert m1.relevant_age_min == 4
    assert m1.relevant_age_max == 12
    assert m1.scores[8].count == 1
    assert np.isclose(m1.scores[8].mean, 1.0)
    assert np.isclose(m1.scores[8].stddev, 0.0)

    assert m2.milestone_id == 2
    assert m2.expected_age == 8
    assert m2.relevant_age_min == 4
    assert m2.relevant_age_max == 12
    assert m2.scores[8].count == 1
    assert np.isclose(m2.scores[8].mean, 0.0)
    assert np.isclose(m2.scores[8].stddev, 0.0)

    # updated stats (answer sessions 1, 2, 4)
    await async_update_stats(session, user_session)
    m1 = session.get(MilestoneAgeScoreCollection, 1)
    m2 = session.get(MilestoneAgeScoreCollection, 2)

    assert m1.milestone_id == 1
    # not enough stats to calculate expected age so get max age as a default
    assert m1.expected_age == 72
    assert m1.relevant_age_min == 0
    assert m1.relevant_age_max == 72
    assert m1.scores[8].count == 3
    m1_scores = [1, 1, 2]
    assert m1.scores[8].mean == pytest.approx(np.mean(m1_scores))
    assert m1.scores[8].stddev == pytest.approx(np.std(m1_scores, ddof=1))

    assert m2.milestone_id == 2
    assert m2.expected_age == 72
    assert m2.relevant_age_min == 0
    assert m2.relevant_age_max == 72
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

    # updated stats (answer sessions 1, 2, 4)
    updated_answers = answers + [np.mean([1, 1, 0])] + [np.mean([2, 0, 0])]
    await async_update_stats(session, user_session)
    mg = session.get(MilestoneGroupAgeScoreCollection, 1)

    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == len(updated_answers)
    assert np.isclose(mg.scores[8].mean, np.mean(updated_answers))
    assert mg.scores[8].stddev == pytest.approx(np.std(updated_answers, ddof=1))


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
