import numpy as np
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import _get_average_scores_by_age
from mondey_backend.routers.utils import calculate_milestone_age_scores
from mondey_backend.routers.utils import calculate_milestone_group_age_scores


def test_compute_feedback_simple():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1, age_months=8, avg_score=2.0, sigma_score=0.8, expected_score=1.0
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_compute_feedback_simple_bad_data():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1, age_months=8, avg_score=2.0, sigma_score=0, expected_score=1.0
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1

    dummy_scores.avg_score = 0
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == 1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 1

    score = 2
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_get_answer_session_child_ages_in_months(session):
    child_ages = _get_answer_session_child_ages_in_months(session)
    assert len(child_ages) == 3
    assert child_ages[2] == 9
    assert child_ages[1] == 8
    assert child_ages[3] == 42


def test_get_average_scores_by_age(session):
    answers = session.exec(select(MilestoneAnswer)).all()
    child_ages = {1: 5, 2: 3, 3: 8}

    avg, sigma = _get_average_scores_by_age(answers, child_ages)

    assert avg[5] == 1.5
    assert avg[3] == 3.5
    assert avg[8] == 3.0

    assert sigma[5] == np.std(
        [answer.answer + 1 for answer in answers if answer.answer_session_id == 1],
        ddof=1,
    )

    assert sigma[3] == np.std(
        [answer.answer + 1 for answer in answers if answer.answer_session_id == 2],
        ddof=1,
    )

    assert sigma[8] == np.nan_to_num(
        np.std(
            [answer.answer + 1 for answer in answers if answer.answer_session_id == 3],
            ddof=1,
        )
    )

    child_ages = {}  # no answer sessions ==> empty child ages
    avg, sigma = _get_average_scores_by_age(answers, child_ages)
    assert np.all(avg == 0)
    assert np.all(sigma == 0)

    child_ages = {1: 5, 2: 3, 3: 8}
    answers = []  # no answers ==> empty answers
    avg, sigma = _get_average_scores_by_age(answers, child_ages)
    assert np.all(avg == 0)
    assert np.all(sigma == 0)


def test_calculate_milestone_age_scores(session):
    # calculate_milestone_age_scores
    mscore = calculate_milestone_age_scores(session, 1)

    # only some are filled
    assert mscore.scores[8].avg_score == 2.0
    assert mscore.scores[8].sigma_score == 0.0
    assert mscore.scores[9].avg_score == 4.0
    assert mscore.scores[9].sigma_score == 0.0

    for score in mscore.scores:
        if score.age_months not in [8, 9]:
            assert score.avg_score == 0.0
            assert score.sigma_score == 0.0

    # get milestoneanswersession #1
    answersession = session.exec(select(MilestoneAnswerSession)).first()
    mscore = calculate_milestone_age_scores(
        session, 1, answers=answersession.answers.values()
    )
    assert mscore.scores[8].avg_score == 2.0
    assert mscore.scores[8].sigma_score == 0

    for score in mscore.scores:
        if score.age_months not in [8]:
            assert score.avg_score == 0.0
            assert score.sigma_score == 0.0


def test_calculate_milestone_group_age_scores(session):
    age = 8
    age_lower = 6
    age_upper = 11
    milestone_group_id = 1

    milestone_group = session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == 1)
    ).first()
    milestones = [m.id for m in milestone_group.milestones]
    answers = [
        a.answer
        for a in session.exec(select(MilestoneAnswer)).all()
        if a.milestone_id in milestones
    ]
    score = calculate_milestone_group_age_scores(
        session, milestone_group_id, age, age_lower, age_upper
    )
    assert score.age_months == 8
    assert score.group_id == 1
    assert score.avg_score == 2.5
    assert score.sigma_score == np.std(
        answers,
        ddof=1,
    )

    answersession = session.exec(select(MilestoneAnswerSession)).first()
    answers = [
        a
        for a in session.exec(select(MilestoneAnswer)).all()
        if a.milestone_id in milestones and a.answer_session_id == answersession.id
    ]
    score = calculate_milestone_group_age_scores(
        session, milestone_group_id, age, age_lower, age_upper, answers=answers
    )
    assert score.age_months == 8
    assert score.group_id == 1
    assert score.avg_score == 2.0
    assert score.sigma_score == 0.0
