import datetime

import numpy as np
import pytest
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.statistics import _add_sample
from mondey_backend.routers.statistics import _finalize_statistics
from mondey_backend.routers.statistics import _get_statistics_by_age
from mondey_backend.routers.statistics import calculate_milestone_statistics_by_age
from mondey_backend.routers.statistics import calculate_milestonegroup_statistics_by_age


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

    child_ages = {1: 5, 2: 3, 3: 8}
    answers = []  # no answers ==> empty answers
    count, avg, stddev = _get_statistics_by_age(answers, child_ages)
    assert np.all(count == 0)
    assert np.all(np.isclose(avg, 0))
    assert np.all(np.isclose(stddev, 0))


def test_calculate_milestone_statistics_by_age(statistics_session):
    # calculate_milestone_statistics_by_age
    mscore = calculate_milestone_statistics_by_age(statistics_session, 1)

    # old statistics has avg[age=8] = 3.0 and stddev[age=8] = 0.35, and we
    # get one more answer from answersession 4 with answer = 3
    assert mscore.milestone_id == 1
    assert mscore.scores[8].count == 13
    assert np.isclose(mscore.scores[8].avg_score, 3.0769)
    assert np.isclose(mscore.scores[8].stddev_score, 0.27735)

    # we have nothing new for everything else
    for age in range(0, len(mscore.scores)):
        if age != 8:
            assert mscore.scores[age].count == 12
            avg = 0 if age < 5 else min(1 * age - 5, 3)
            assert np.isclose(mscore.scores[age].avg_score, avg)
            stddev = 0.0 if age < 5 or age >= 8 else 0.35
            assert np.isclose(mscore.scores[age].stddev_score, stddev)

        if age < 8:
            assert mscore.scores[age].expected_score == 1
        else:
            assert mscore.scores[age].expected_score == 4


def test_calculate_milestonegroup_statistics(statistics_session):
    milestone_group = statistics_session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == 1)
    ).first()

    score = calculate_milestonegroup_statistics_by_age(
        statistics_session,
        milestone_group.id,
    )

    assert score.milestone_group_id == 1
    # no change for these ages
    assert np.isclose(score.scores[5].avg_score, 1.2)
    assert np.isclose(score.scores[6].avg_score, 1.44)
    assert np.isclose(score.scores[7].avg_score, 1.68)
    assert np.isclose(score.scores[9].avg_score, 2.16)
    assert np.isclose(score.scores[10].avg_score, 2.4)
    assert np.isclose(score.scores[11].avg_score, 2.64)
    assert np.isclose(score.scores[12].avg_score, 2.88)

    for age in [
        5,
        6,
        7,
    ]:
        assert np.isclose(score.scores[age].count, 4)  # no change for this age
        assert np.isclose(
            score.scores[age].stddev_score, 0.21
        )  # no change for this age

    assert score.scores[8].count == 6
    assert np.isclose(
        score.scores[8].avg_score, 2.446666
    )  # new answers from answersession 4 -> changed value
    assert np.isclose(
        score.scores[8].stddev_score, 0.890037
    )  # new answers from answersession 4 -> changed value
    assert score.scores[8].age == 8
    assert score.scores[8].milestone_group_id == 1
    assert score.created_at - datetime.datetime.now() < datetime.timedelta(
        minutes=1
    )  # allow for very slow machine in CI

    for age in range(0, len(score.scores)):
        if age not in [5, 6, 7, 8]:
            assert score.scores[age].count == 0
        if age > 12:
            assert np.isclose(score.scores[age].avg_score, 3.0)
