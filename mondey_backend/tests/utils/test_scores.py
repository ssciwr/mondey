from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.routers.scores import compute_feedback_simple


def test_compute_milestone_statistics():
    dummy_scores = MilestoneAgeScore(
        milestone_id=1, age_months=8, avg_score=2.0, sigma_score=0.8, expected_score=1.0
    )
    score = 0
    assert compute_feedback_simple(dummy_scores, score) == -1

    score = 1
    assert compute_feedback_simple(dummy_scores, score) == 0

    score = 3
    assert compute_feedback_simple(dummy_scores, score) == 1


def test_compute_milestone_statistics_bad_data():
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


# def test_compute_milestonegroup_statistics():
#     # calculate_milestone_group_age_scores

#     assert 3 == 6

# def test_compute_milestonegroup_statistics_bad_data():
#     # calculate_milestone_group_age_scores
#     assert 3 == 6

# def test_compute_feedback_simple():
#     # compute_feedback_simple
#     assert 3 == 6

# def test_compute_milestonegroup_feedback():
#     # compute_feedback_for_milestonegroup
#     assert 3 == 6
