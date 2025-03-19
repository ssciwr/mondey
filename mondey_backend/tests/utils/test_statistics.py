import numpy as np
import pytest
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.statistics import _add_sample
from mondey_backend.statistics import _finalize_statistics
from mondey_backend.statistics import _get_statistics_by_age
from mondey_backend.statistics import async_update_stats


def test_online_statistics_computation():
    data = np.random.normal(0, 1, 200)
    data_first = data[0:100]
    data_second = data[100:200]

    count = 0
    avg = 0.0
    var = 0.0

    for v in data_first:
        count, avg, var = _add_sample(count, avg, var, v)

    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == len(data_first)
    assert np.isclose(avg, np.mean(data_first))
    assert np.isclose(std, np.std(data_first, ddof=1))

    for v in data_second:
        count, avg, var = _add_sample(count, avg, var, v)

    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == len(data)
    assert np.isclose(avg, np.mean(data))
    assert np.isclose(std, np.std(data, ddof=1))


def test_online_statistics_computation_too_little_data():
    data = [
        2.42342,
    ]
    count = 0
    avg = 0
    var = 0
    for v in data:
        count, avg, var = _add_sample(count, avg, var, v)
    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == 1
    assert np.isclose(avg, 2.42342)
    assert std == 0

    data = np.array([])
    count = 0
    avg = 0.0
    var = 0.0
    for v in data:
        count, avg, var = _add_sample(count, avg, var, v)
    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == 0
    assert avg == 0
    assert std == 0

    data = [1, 2, 3]
    count = 0
    avg = 0
    var = 0
    for v in data:
        count, avg, var = _add_sample(count, avg, var, v)

    var = set(
        [
            var,
        ]
    )  # wrong type
    with pytest.raises(
        ValueError,
        match="Given values for statistics computation must be of type int|float|np.ndarray",
    ):
        count, avg, std = _finalize_statistics(count, avg, var)


def test_get_score_statistics_by_age(session):
    answers = session.exec(select(MilestoneAnswer)).all()
    # which answers we choose here is arbitrary for testing, we just need to make sure it's fixed and not empty
    child_ages = {
        1: 5,
        2: 3,
        3: 8,
        4: 11,
        99: 60,
    }

    count, avg, stddev = _get_statistics_by_age(answers, child_ages)

    answers_5 = [
        answer.answer + 1 for answer in answers if answer.answer_session_id == 1
    ]
    answers_3 = [
        answer.answer + 1 for answer in answers if answer.answer_session_id == 2
    ]
    answers_8 = [
        answer.answer + 1 for answer in answers if answer.answer_session_id == 3
    ]

    assert count[5] == 2
    assert count[3] == 2
    assert count[8] == 1

    assert np.isclose(avg[5], 1.5)
    assert np.isclose(avg[3], 3.5)
    assert np.isclose(avg[8], 3.0)

    assert np.isclose(
        stddev[5],
        np.std(
            answers_5,
            ddof=1,
        ),
    )

    assert np.isclose(
        stddev[3],
        np.std(
            answers_3,
            ddof=1,
        ),
    )

    assert np.isclose(
        stddev[8],
        np.nan_to_num(
            np.std(
                answers_8,
                ddof=1,
            )
        ),
    )

    # check that updating works correctly. This is not done for all sessions
    second_answers = answers
    for answer in second_answers:
        answer.answer += 1 if answer.answer != 3 else -1
    answers_5.extend(
        [
            answer.answer + 1
            for answer in second_answers
            if answer.answer_session_id in [1, 4]
        ]
    )
    answers_3.extend(
        [
            answer.answer + 1
            for answer in second_answers
            if answer.answer_session_id == 2
        ]
    )
    answers_8.extend(
        [
            answer.answer + 1
            for answer in second_answers
            if answer.answer_session_id == 3
        ]
    )

    count, avg, stddev = _get_statistics_by_age(
        second_answers, child_ages, count, avg, stddev
    )

    assert count[5] == 4
    assert count[3] == 4
    assert count[8] == 2
    assert np.isclose(avg[5], np.mean(answers_5))
    assert np.isclose(avg[3], np.mean(answers_3))
    assert np.isclose(avg[8], np.mean(answers_8))

    assert np.isclose(stddev[5], np.std(answers_5, ddof=1))
    assert np.isclose(stddev[3], np.std(answers_3, ddof=1))
    assert np.isclose(stddev[8], np.std(answers_8, ddof=1))


def test_get_score_statistics_by_age_no_data(statistics_session):
    answers = statistics_session.exec(select(MilestoneAnswer)).all()
    child_ages = {}  # no answer sessions ==> empty child ages
    count, avg, stddev = _get_statistics_by_age(answers, child_ages)
    assert np.all(np.isclose(avg, 0))
    assert np.all(np.isclose(stddev, 0))

    child_ages = {1: 5, 2: 3, 3: 8, 4: 11, 99: 60}
    answers = []  # no answers ==> empty answers
    count, avg, stddev = _get_statistics_by_age(answers, child_ages)
    assert np.all(count == 0)
    assert np.all(np.isclose(avg, 0))
    assert np.all(np.isclose(stddev, 0))


@pytest.mark.asyncio
async def test_calculate_milestone_statistics_by_age(statistics_session, user_session):
    m1 = statistics_session.get(MilestoneAgeScoreCollection, 1)
    m2 = statistics_session.get(MilestoneAgeScoreCollection, 2)

    # existing stats (only answer session 1)
    assert m1.milestone_id == 1
    assert m1.scores[8].count == 1
    assert np.isclose(m1.scores[8].avg_score, 2.0)
    assert np.isclose(m1.scores[8].stddev_score, 0.0)

    assert m2.milestone_id == 2
    assert m2.scores[8].count == 1
    assert np.isclose(m2.scores[8].avg_score, 1.0)
    assert np.isclose(m2.scores[8].stddev_score, 0.0)

    # updated stats (answer sessions 1, 2, 4)
    await async_update_stats(statistics_session, user_session, incremental_update=True)
    m1 = statistics_session.get(MilestoneAgeScoreCollection, 1)
    m2 = statistics_session.get(MilestoneAgeScoreCollection, 2)

    assert m1.milestone_id == 1
    assert m1.scores[8].count == 3
    assert np.isclose(m1.scores[8].avg_score, (2 + 4 + 4) / 3.0)
    assert m1.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)

    assert m2.milestone_id == 2
    assert m2.scores[8].count == 3
    assert np.isclose(m2.scores[8].avg_score, (1 + 3 + 3) / 3.0)
    assert m2.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)

    # re-calculating using all answers gives the same results
    await async_update_stats(statistics_session, user_session, incremental_update=False)
    m1 = statistics_session.get(MilestoneAgeScoreCollection, 1)
    m2 = statistics_session.get(MilestoneAgeScoreCollection, 2)

    assert m1.milestone_id == 1
    assert m1.scores[8].count == 3
    assert np.isclose(m1.scores[8].avg_score, (2 + 4 + 4) / 3.0)
    assert m1.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)

    assert m2.milestone_id == 2
    assert m2.scores[8].count == 3
    assert np.isclose(m2.scores[8].avg_score, (1 + 3 + 3) / 3.0)
    assert m2.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)


@pytest.mark.asyncio
async def test_calculate_milestonegroup_statistics(statistics_session, user_session):
    mg = statistics_session.get(MilestoneGroupAgeScoreCollection, 1)

    # existing stats (only answer session 1)
    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == 2
    assert np.isclose(mg.scores[8].avg_score, (1 + 2) / 2.0)
    assert np.isclose(mg.scores[8].stddev_score, 0.5)

    # updated stats (answer sessions 1, 2, 4)
    await async_update_stats(statistics_session, user_session, incremental_update=True)
    mg = statistics_session.get(MilestoneGroupAgeScoreCollection, 1)

    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == 6
    assert np.isclose(mg.scores[8].avg_score, (1 + 2 + 3 + 4 + 3 + 4) / 6.0)
    assert mg.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)

    # re-calculating using all answers gives the same results
    await async_update_stats(statistics_session, user_session, incremental_update=False)
    mg = statistics_session.get(MilestoneGroupAgeScoreCollection, 1)

    assert mg.milestone_group_id == 1
    assert mg.scores[8].count == 6
    assert np.isclose(mg.scores[8].avg_score, (1 + 2 + 3 + 4 + 3 + 4) / 6.0)
    assert mg.scores[8].stddev_score == pytest.approx(1.15, abs=0.1)
