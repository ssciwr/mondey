import numpy as np
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
    avg = 0
    var = 0

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
    data = [2.42342]
    count = 0
    avg = 0
    var = 0
    for v in data:
        count, avg, var = _add_sample(count, avg, var, v)
    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == 1
    assert avg == 2.42342
    assert std == 0

    data = []
    count = 0
    avg = 0
    var = 0
    for v in data:
        count, avg, var = _add_sample(count, avg, var, v)
    count, avg, std = _finalize_statistics(count, avg, var)

    assert count == 0
    assert avg == 0
    assert std == 0


def test_get_score_statistics_by_age(session):
    answers = session.exec(select(MilestoneAnswer)).all()
    child_ages = {1: 5, 2: 3, 3: 8}

    count, avg, stddev = _get_statistics_by_age(answers, child_ages)

    assert count[5] == 2
    assert count[3] == 2
    assert count[8] == 1
    assert np.isclose(avg[5], 1.5)
    assert np.isclose(avg[3], 3.5)
    assert np.isclose(avg[8], 3.0)

    assert np.isclose(
        stddev[5],
        np.std(
            [answer.answer + 1 for answer in answers if answer.answer_session_id == 1],
            ddof=1,
        ),
    )

    assert np.isclose(
        stddev[3],
        np.std(
            [answer.answer + 1 for answer in answers if answer.answer_session_id == 2],
            ddof=1,
        ),
    )

    assert np.isclose(
        stddev[8],
        np.nan_to_num(
            np.std(
                [
                    answer.answer + 1
                    for answer in answers
                    if answer.answer_session_id == 3
                ],
                ddof=1,
            )
        ),
    )


def test_get_score_statistics_by_age_no_data(session):
    answers = session.exec(select(MilestoneAnswer)).all()
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


def test_calculate_milestone_statistics_by_age(session):
    # calculate_milestone_statistics_by_age
    mscore = calculate_milestone_statistics_by_age(session, 1)

    # only some are filled: milestone 1 is part of answersession 1 (age 8) and 2 (age 9) with
    # answers 1, 3 => 2, 4 hence std = 0 and avg = answers + 1
    # only answersession 2 is relevant because it was created yesterday by definition, the rest stays the same.
    # it only has one answer for milestone 1
    assert mscore.milestone_id == 1
    assert mscore.scores[8].count == 2
    assert np.isclose(mscore.scores[8].avg_score, 1.5)
    assert np.isclose(mscore.scores[8].stddev_score, 0.702)

    assert mscore.scores[9].count == 3
    assert np.isclose(mscore.scores[9].avg_score, 2.333333, atol=1e-6)
    assert np.isclose(mscore.scores[9].stddev_score, 1.526347, atol=1e-6)

    assert mscore.scores[42].count == 0
    assert np.isclose(mscore.scores[42].avg_score, 0.0)
    assert np.isclose(mscore.scores[42].stddev_score, 0.0)

    for score in mscore.scores:
        if score.age not in [8, 9]:
            assert score.count == 0
            assert np.isclose(score.avg_score, 0.0)
            assert np.isclose(score.stddev_score, 0.0)


def test_calculate_milestonegroup_statistics(session):
    milestone_group = session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == 1)
    ).first()

    # only answersession 2 is relevant because it has been created today per definition
    # answersession 2 with age 9 has answers 3, 4 after +1 correction
    # ==> only age 9 values change, everything else stays as is

    # answersession 3 with age 42 has no answers for milestonegroup 1
    score = calculate_milestonegroup_statistics_by_age(
        session,
        milestone_group.id,
    )

    assert score.milestone_group_id == 1
    assert score.scores[8].count == 2
    assert np.isclose(score.scores[8].avg_score, 2.3)
    assert np.isclose(score.scores[8].stddev_score, 0.45)
    assert score.scores[8].age == 8
    assert score.scores[8].milestone_group_id == 1

    assert score.scores[9].count == 4
    assert np.isclose(score.scores[9].avg_score, 2.9)
    assert np.isclose(score.scores[9].stddev_score, 0.845083)
    assert score.scores[9].age == 9
    assert score.scores[9].milestone_group_id == 1

    for age in range(0, len(score.scores)):
        if age not in [8, 9]:
            assert score.scores[age].count == 0
            assert score.scores[age].avg_score == 0
            assert score.scores[age].stddev_score == 0
            assert score.scores[age].milestone_group_id == 1
