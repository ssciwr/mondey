import numpy as np
from sqlalchemy import select

from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.routers.scores import compute_feedback_simple
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import _get_average_scores_by_age
from mondey_backend.routers.utils import calculate_milestone_age_scores


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

    # TODO: check what can go wrong here


def test_get_average_scores_by_age(session):
    answers = [answer[0] for answer in session.exec(select(MilestoneAnswer)).all()]
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
            [answer.answer + 1 for answer in answers if answer.answer_session_id == 2],
            ddof=1,
        )
    )


def test_calculate_milestone_age_scores(session):
    # calculate_milestone_age_scores

    mscore = calculate_milestone_age_scores(session, 1)

    for m in mscore.scores:
        print(m)

    assert 3 == 6


# def test_compute_milestonegroup_statistics():
#     # calculate_milestone_group_age_scores

#     assert 3 == 6

# def test_compute_milestonegroup_statistics_bad_data():
#     # calculate_milestone_group_age_scores
#     assert 3 == 6

# def test_compute_milestonegroup_feedback():
#     # compute_feedback_for_milestonegroup
#     assert 3 == 6
