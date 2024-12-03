import numpy as np
from numpy import isclose
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import _get_statistics_by_age
from mondey_backend.routers.utils import calculate_milestone_statistics_by_age
from mondey_backend.routers.utils import calculate_milestonegroup_statistics_by_age
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
    child_ages = _get_answer_session_child_ages_in_months(session)
    assert len(child_ages) == 3
    assert child_ages[2] == 9
    assert child_ages[1] == 8
    assert child_ages[3] == 42


def test_get_score_statistics_by_age(session):
    answers = session.exec(select(MilestoneAnswer)).all()
    child_ages = {1: 5, 2: 3, 3: 8}

    avg, stddev = _get_statistics_by_age(answers, child_ages)

    assert isclose(avg[5], 1.5)
    assert isclose(avg[3], 3.5)
    assert isclose(avg[8], 3.0)

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

    child_ages = {}  # no answer sessions ==> empty child ages
    avg, stddev = _get_statistics_by_age(answers, child_ages)
    assert np.all(np.isclose(avg, 0))
    assert np.all(np.isclose(stddev, 0))

    child_ages = {1: 5, 2: 3, 3: 8}
    answers = []  # no answers ==> empty answers
    avg, stddev = _get_statistics_by_age(answers, child_ages)
    assert np.all(np.isclose(avg, 0))
    assert np.all(np.isclose(stddev, 0))


def test_calculate_milestone_statistics_by_age(session):
    # calculate_milestone_statistics_by_age
    mscore = calculate_milestone_statistics_by_age(session, 1)

    # only some are filled: milestone 1 is part of answersession 1 (age 8) and 2 (age 9) with
    # answers 1, 3 => 2, 4 hence std = 0 and avg = answers + 1
    assert mscore.milestone_id == 1
    assert np.isclose(mscore.scores[8].avg_score, 2.0)
    assert np.isclose(mscore.scores[8].stddev_score, 0.0)
    assert np.isclose(mscore.scores[9].avg_score, 4.0)
    assert np.isclose(mscore.scores[9].stddev_score, 0.0)
    assert np.isclose(mscore.scores[42].avg_score, 0.0)
    assert np.isclose(mscore.scores[42].stddev_score, 0.0)

    for score in mscore.scores:
        if score.age_months not in [8, 9]:
            assert np.isclose(score.avg_score, 0.0)
            assert np.isclose(score.stddev_score, 0.0)

        if score.age_months > 8:
            assert np.isclose(score.expected_score, 4.0)
        else:
            assert np.isclose(score.expected_score, 1.0)


def test_calculate_milestonegroup_statistics(session):
    milestone_group = session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == 1)
    ).first()

    # milestonegroup 1 has 2 milestones (1, 2 with answers 1, 0 --> 2, 1,
    # this belongs wholely to answersession 1 with age 8
    avg_1 = np.mean([1, 2])
    std_1 = np.std([1, 2], ddof=1)
    # milestonegroup 2 has 2 milestones (1, 2 with answers 3, 2 --> 4, 3
    # this belongs wholely to answersession 2 with age 9
    avg_2 = np.mean([4, 3])
    std_2 = np.std([4, 3], ddof=1)

    # answersession 3 with age 42 has no answers for milestonegroup 1

    score = calculate_milestonegroup_statistics_by_age(
        session,
        milestone_group.id,
    )

    assert score.milestonegroup_id == 1
    assert score.scores[8].avg_score == avg_1
    assert score.scores[8].stddev_score == std_1
    assert score.scores[8].age_months == 8
    assert score.scores[8].milestonegroup_id == 1

    assert score.scores[9].avg_score == avg_2
    assert score.scores[9].stddev_score == std_2
    assert score.scores[9].age_months == 9
    assert score.scores[9].milestonegroup_id == 1

    for age in range(0, len(score.scores)):
        if age not in [8, 9]:
            assert score.scores[age].avg_score == 0
            assert score.scores[age].stddev_score == 0
            assert score.scores[age].milestonegroup_id == 1
