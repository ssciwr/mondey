import numpy as np
import pytest

from mondey_backend.routers.utils import MEAN_ANSWER_ACHIEVED
from mondey_backend.routers.utils import MilestoneAgeCurve
from mondey_backend.routers.utils import fit_milestone_age_curve
from mondey_backend.routers.utils import get_milestone_ages_from_curve
from mondey_backend.settings import app_settings


def make_counts(
    answers_by_age: dict[int, list[int]],
) -> np.ndarray:
    """Build a (age, answer) count array from {age: [n0, n1, n2, n3]}."""
    counts = np.zeros((app_settings.MAX_CHILD_AGE_MONTHS + 1, 4), dtype=np.uint64)
    for age, answers in answers_by_age.items():
        counts[age] = answers
    return counts


def counts_from_curve(
    expected_age: float, steepness: float, n_per_age: int = 20
) -> np.ndarray:
    """Sample answer counts from a known logistic curve, so a fit can recover it."""
    midpoint = (
        expected_age
        - np.log(MEAN_ANSWER_ACHIEVED / (3.0 - MEAN_ANSWER_ACHIEVED)) / steepness
    )
    counts = np.zeros((app_settings.MAX_CHILD_AGE_MONTHS + 1, 4), dtype=np.uint64)
    for age in range(app_settings.MAX_CHILD_AGE_MONTHS + 1):
        mean_answer = 3.0 / (1.0 + np.exp(-steepness * (age - midpoint)))
        # split n_per_age answers between the two answers either side of the mean
        lower = int(np.floor(mean_answer))
        upper = min(lower + 1, 3)
        frac = mean_answer - lower
        counts[age][upper] += round(n_per_age * frac)
        counts[age][lower] += n_per_age - round(n_per_age * frac)
    return counts


@pytest.mark.parametrize(
    ("expected_age", "steepness"),
    [(12.0, 0.4), (37.0, 0.2), (55.0, 0.3)],
)
def test_fit_recovers_known_curve(expected_age: float, steepness: float):
    curve = fit_milestone_age_curve(counts_from_curve(expected_age, steepness))
    assert curve.fit_ok
    assert curve.expected_age == pytest.approx(expected_age, abs=1.0)
    assert curve.steepness == pytest.approx(steepness, abs=0.05)


def test_fit_mean_answer_is_monotonic_and_within_range():
    curve = fit_milestone_age_curve(counts_from_curve(24.0, 0.3))
    ages = np.arange(0, app_settings.MAX_CHILD_AGE_MONTHS + 1)
    mean_answers = curve.mean_answer(ages)
    assert np.all(np.diff(mean_answers) > 0)
    assert np.all(mean_answers > 0)
    assert np.all(mean_answers < 3)


def test_expected_age_is_where_curve_reaches_achieved():
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))
    assert curve.mean_answer(curve.expected_age) == pytest.approx(MEAN_ANSWER_ACHIEVED)


def test_fit_rejected_if_too_few_answers():
    # a perfectly shaped curve, but sampled too sparsely to be trusted
    counts = counts_from_curve(24.0, 0.3, n_per_age=1)
    curve = fit_milestone_age_curve(counts)
    assert curve.n_answers < app_settings.MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT
    assert not curve.fit_ok


def test_fit_rejected_if_answers_at_only_one_age():
    curve = fit_milestone_age_curve(make_counts({8: [50, 50, 50, 50]}))
    assert not curve.fit_ok


def test_fit_rejected_if_no_transition_in_age_range():
    # every child of every age has achieved the milestone, so there is no transition to
    # locate and the fitted parameters would be meaningless
    counts = make_counts({age: [0, 0, 0, 20] for age in range(0, 73)})
    curve = fit_milestone_age_curve(counts)
    assert not curve.fit_ok


def test_fit_rejected_if_achievement_is_beyond_age_range():
    # The answers cross the midpoint, but remain below the achieved threshold at the
    # oldest supported age. The constrained optimizer must not turn this into an
    # achievement at exactly the upper age bound.
    counts = counts_from_curve(expected_age=80.0, steepness=0.1)
    mean_answers = (counts @ np.arange(4)) / counts.sum(axis=1)
    assert mean_answers.min() < 1.5 < mean_answers.max()
    assert mean_answers[-1] < MEAN_ANSWER_ACHIEVED

    curve = fit_milestone_age_curve(counts)
    assert not curve.fit_ok


def test_ages_fall_back_to_heuristic_if_fit_rejected():
    # too few answers to fit, but enough for the heuristic to consider it achieved at 8
    counts = make_counts({age: [0, 0, 0, 5] for age in range(8, 73)})
    curve = fit_milestone_age_curve(counts)
    assert not curve.fit_ok
    expected_age, relevant_age_min, relevant_age_max = get_milestone_ages_from_curve(
        curve, counts
    )
    assert expected_age == 8


def test_ages_from_curve_are_ordered_and_clamped():
    counts = counts_from_curve(30.0, 0.3)
    curve = fit_milestone_age_curve(counts)
    assert curve.fit_ok
    expected_age, relevant_age_min, relevant_age_max = get_milestone_ages_from_curve(
        curve, counts
    )
    assert 0 <= relevant_age_min < expected_age < relevant_age_max
    assert relevant_age_max <= app_settings.MAX_CHILD_AGE_MONTHS


def test_curve_round_trips_exactly_through_midpoint():
    """
    The stored midpoint must reconstruct the fitted curve exactly, so that the answers
    imputed when giving feedback for a child match those the statistics were built from.
    The stored expected_age is rounded to whole months and so cannot be used for this.
    """
    fitted = fit_milestone_age_curve(counts_from_curve(15.3, 0.44))
    assert fitted.fit_ok
    reconstructed = MilestoneAgeCurve.from_midpoint(
        midpoint=fitted.midpoint,
        steepness=fitted.steepness,
        n_answers=fitted.n_answers,
    )
    assert reconstructed.expected_age == pytest.approx(fitted.expected_age)
    for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
        assert reconstructed.mean_answer(age) == pytest.approx(fitted.mean_answer(age))


def test_fit_is_robust_to_a_noisy_sparse_age():
    """A single age with few, unrepresentative answers must not drag the curve."""
    counts = counts_from_curve(30.0, 0.3)
    clean = fit_milestone_age_curve(counts)
    # two children of age 2 whose parents claim the milestone is fully achieved
    counts[2] = [0, 0, 0, 2]
    noisy = fit_milestone_age_curve(counts)
    assert noisy.fit_ok
    assert noisy.expected_age == pytest.approx(clean.expected_age, abs=1.0)
