import numpy as np
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import _get_score_statistics_by_age
from mondey_backend.routers.utils import calculate_milestone_statistics_by_age
from mondey_backend.routers.utils import calculate_milestonegroup_statistics


def test_get_answer_session_child_ages_in_months(session):
    child_ages = _get_answer_session_child_ages_in_months(session)
    assert len(child_ages) == 3
    assert child_ages[2] == 9
    assert child_ages[1] == 8
    assert child_ages[3] == 42


def test_get_score_statistics_by_age(session):
    answers = session.exec(select(MilestoneAnswer)).all()
    child_ages = {1: 5, 2: 3, 3: 8}

    avg, stddev = _get_score_statistics_by_age(answers, child_ages)

    assert avg[5] == 1.5
    assert avg[3] == 3.5
    assert avg[8] == 3.0

    assert stddev[5] == np.std(
        [answer.answer + 1 for answer in answers if answer.answer_session_id == 1],
        ddof=1,
    )

    assert stddev[3] == np.std(
        [answer.answer + 1 for answer in answers if answer.answer_session_id == 2],
        ddof=1,
    )

    assert stddev[8] == np.nan_to_num(
        np.std(
            [answer.answer + 1 for answer in answers if answer.answer_session_id == 3],
            ddof=1,
        )
    )

    child_ages = {}  # no answer sessions ==> empty child ages
    avg, stddev = _get_score_statistics_by_age(answers, child_ages)
    assert np.all(avg == 0)
    assert np.all(stddev == 0)

    child_ages = {1: 5, 2: 3, 3: 8}
    answers = []  # no answers ==> empty answers
    avg, stddev = _get_score_statistics_by_age(answers, child_ages)
    assert np.all(avg == 0)
    assert np.all(stddev == 0)


def test_calculate_milestone_statistics_by_age(session):
    # calculate_milestone_statistics_by_age
    mscore = calculate_milestone_statistics_by_age(session, 1)

    # only some are filled
    assert mscore.scores[8].avg_score == 2.0
    assert mscore.scores[8].stddev_score == 0.0
    assert mscore.scores[9].avg_score == 4.0
    assert mscore.scores[9].stddev_score == 0.0

    for score in mscore.scores:
        if score.age_months not in [8, 9]:
            assert score.avg_score == 0.0
            assert score.stddev_score == 0.0


def test_calculate_milestonegroup_statistics(session):
    age = 8
    age_lower = 6
    age_upper = 11

    milestone_group = session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == 1)
    ).first()
    milestones = [m.id for m in milestone_group.milestones]
    answers = [
        a.answer
        for a in session.exec(select(MilestoneAnswer)).all()
        if a.milestone_id in milestones
    ]
    score = calculate_milestonegroup_statistics(
        session, milestone_group, age, age_lower, age_upper
    )
    assert score.age_months == 8
    assert score.group_id == 1
    assert score.avg_score == 2.5
    assert score.stddev_score == np.std(
        answers,
        correction=1,
    )
