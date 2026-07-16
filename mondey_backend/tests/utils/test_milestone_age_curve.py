import numpy as np
import pytest
from pydantic import ValidationError

from mondey_backend.models.milestones import MilestoneAgeCurveParams
from mondey_backend.routers.utils import MEAN_ANSWER_MIDPOINT
from mondey_backend.routers.utils import MilestoneAgeCurve
from mondey_backend.routers.utils import fit_milestone_age_curve
from mondey_backend.routers.utils import get_milestone_ages_from_curve
from mondey_backend.settings import app_settings

DEFAULT_PARAMS = MilestoneAgeCurveParams()


def make_counts(
    answers_by_age: dict[int, list[int]],
) -> np.ndarray:
    """Build a (age, answer) count array from {age: [n0, n1, n2, n3]}."""
    counts = np.zeros((app_settings.MAX_CHILD_AGE_MONTHS + 1, 4), dtype=np.uint64)
    for age, answers in answers_by_age.items():
        counts[age] = answers
    return counts


def counts_from_curve(
    midpoint: float, steepness: float, n_per_age: int = 20
) -> np.ndarray:
    """Sample answer counts from a known logistic curve, so a fit can recover it."""
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
    ("midpoint", "steepness"),
    [(12.0, 0.4), (37.0, 0.2), (55.0, 0.3)],
)
def test_fit_recovers_known_curve(midpoint: float, steepness: float):
    curve = fit_milestone_age_curve(counts_from_curve(midpoint, steepness))
    assert curve.fit_ok
    assert curve.midpoint == pytest.approx(midpoint, abs=1.0)
    assert curve.steepness == pytest.approx(steepness, abs=0.05)


def test_fit_mean_answer_is_monotonic_and_within_range():
    curve = fit_milestone_age_curve(counts_from_curve(24.0, 0.3))
    ages = np.arange(0, app_settings.MAX_CHILD_AGE_MONTHS + 1)
    mean_answers = curve.mean_answer(ages)
    assert np.all(np.diff(mean_answers) > 0)
    assert np.all(mean_answers > 0)
    assert np.all(mean_answers < 3)


def test_curve_midpoint_is_where_the_mean_answer_is_halfway():
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))
    assert curve.mean_answer(curve.midpoint) == pytest.approx(MEAN_ANSWER_MIDPOINT)
    assert curve.age_at_mean_answer(MEAN_ANSWER_MIDPOINT) == pytest.approx(
        curve.midpoint
    )


@pytest.mark.parametrize(
    "invalid",
    [
        # the achieved threshold has to lie inside the relevant range, so that the
        # expected age lies inside the age range the milestone is asked about in
        {"mean_answer_achieved": 2.9, "mean_answer_relevant_max": 2.7},
        {"mean_answer_achieved": 0.2, "mean_answer_relevant_min": 0.3},
        # the thresholds are mean answers, which have to stay inside (0, 3)
        {"mean_answer_achieved": 3.0},
        {"mean_answer_relevant_min": 0.0},
        {"min_relevant_age_margin_months": -1},
    ],
)
def test_invalid_params_are_rejected(invalid: dict):
    with pytest.raises(ValidationError):
        MilestoneAgeCurveParams(**invalid)


def test_sharp_transition_is_accepted():
    # every child answers 0 before 12 months and 3 from 12 months onwards. A transition
    # this sharp is very well determined, not unresolvable, so it must not be rejected:
    # the minimum relevant age margin is what keeps its age range usable.
    counts = make_counts(
        {age: [50, 0, 0, 0] if age < 12 else [0, 0, 0, 50] for age in range(0, 73)}
    )
    curve = fit_milestone_age_curve(counts)
    assert curve.fit_ok
    assert curve.midpoint == pytest.approx(11.5, abs=0.5)

    expected_age, age_min, age_max = get_milestone_ages_from_curve(
        curve, DEFAULT_PARAMS
    )
    assert expected_age == 12
    margin = DEFAULT_PARAMS.min_relevant_age_margin_months
    assert age_min == expected_age - margin
    assert age_max == expected_age + margin


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


def test_no_ages_if_achievement_is_beyond_age_range():
    # The answers cross the midpoint, so the curve itself is well determined, but they
    # remain below the achieved threshold at the oldest supported age: we cannot say at
    # what age this milestone is achieved, so there is no automatic estimate for it.
    counts = counts_from_curve(midpoint=66.0, steepness=0.1)
    mean_answers = (counts @ np.arange(4)) / counts.sum(axis=1)
    assert mean_answers.min() < MEAN_ANSWER_MIDPOINT < mean_answers.max()
    assert mean_answers[-1] < DEFAULT_PARAMS.mean_answer_achieved

    curve = fit_milestone_age_curve(counts)
    assert curve.fit_ok
    assert curve.age_at_mean_answer(DEFAULT_PARAMS.mean_answer_achieved) > (
        app_settings.MAX_CHILD_AGE_MONTHS
    )
    assert get_milestone_ages_from_curve(curve, DEFAULT_PARAMS) is None
    # lowering the achieved threshold brings it back inside the supported age range
    params = MilestoneAgeCurveParams(mean_answer_achieved=1.8)
    assert get_milestone_ages_from_curve(curve, params) is not None


def test_no_ages_if_fit_rejected():
    # a milestone we cannot fit a curve for has no automatic age estimate at all: the
    # ages set on the milestone by an admin have to be left alone
    counts = make_counts({age: [0, 0, 0, 5] for age in range(8, 73)})
    curve = fit_milestone_age_curve(counts)
    assert not curve.fit_ok
    assert get_milestone_ages_from_curve(curve, DEFAULT_PARAMS) is None
    assert get_milestone_ages_from_curve(None, DEFAULT_PARAMS) is None


def test_ages_from_curve_are_ordered_and_clamped():
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))
    assert curve.fit_ok
    expected_age, relevant_age_min, relevant_age_max = get_milestone_ages_from_curve(
        curve, DEFAULT_PARAMS
    )
    assert 0 <= relevant_age_min < expected_age < relevant_age_max
    assert relevant_age_max <= app_settings.MAX_CHILD_AGE_MONTHS


def test_ages_are_the_ages_at_the_configured_mean_answers():
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))
    params = MilestoneAgeCurveParams(
        mean_answer_achieved=2.0,
        mean_answer_relevant_min=0.5,
        mean_answer_relevant_max=2.5,
        min_relevant_age_margin_months=0,
    )
    ages = get_milestone_ages_from_curve(curve, params)
    assert ages == (
        round(curve.age_at_mean_answer(2.0)),
        round(curve.age_at_mean_answer(0.5)),
        round(curve.age_at_mean_answer(2.5)),
    )


def test_raising_the_achieved_threshold_raises_the_expected_age():
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))

    def expected_age(mean_answer_achieved: float) -> int:
        # the relevant range has to contain every achieved threshold tried below, since
        # the expected age has to lie inside the relevant age range
        params = MilestoneAgeCurveParams(
            mean_answer_achieved=mean_answer_achieved,
            mean_answer_relevant_min=0.3,
            mean_answer_relevant_max=2.95,
        )
        ages = get_milestone_ages_from_curve(curve, params)
        assert ages is not None
        return ages[0]

    assert expected_age(1.5) < expected_age(2.4) < expected_age(2.9)


def test_relevant_age_range_covers_the_margin_around_the_expected_age():
    # a steep curve crosses both relevant thresholds within a couple of months
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 1.5))
    assert curve.fit_ok
    params = MilestoneAgeCurveParams(min_relevant_age_margin_months=9)
    expected_age, relevant_age_min, relevant_age_max = get_milestone_ages_from_curve(
        curve, params
    )
    assert relevant_age_min <= expected_age - 9
    assert relevant_age_max >= expected_age + 9


def test_margin_only_widens_the_relevant_age_range():
    """The margin must not move the expected age, or narrow a wide enough range."""
    curve = fit_milestone_age_curve(counts_from_curve(30.0, 0.3))
    without_margin = get_milestone_ages_from_curve(
        curve, MilestoneAgeCurveParams(min_relevant_age_margin_months=0)
    )
    with_margin = get_milestone_ages_from_curve(
        curve, MilestoneAgeCurveParams(min_relevant_age_margin_months=24)
    )
    assert without_margin is not None
    assert with_margin is not None
    assert with_margin[0] == without_margin[0]
    assert with_margin[1] < without_margin[1]
    assert with_margin[2] > without_margin[2]

    # a gradual curve already spans more than the margin, so nothing changes
    unchanged = get_milestone_ages_from_curve(
        curve, MilestoneAgeCurveParams(min_relevant_age_margin_months=1)
    )
    assert unchanged == without_margin


def test_relevant_age_range_is_clamped_to_the_supported_ages():
    # a milestone achieved so early that the margin reaches back before birth
    curve = fit_milestone_age_curve(counts_from_curve(1.0, 1.5))
    assert curve.fit_ok
    params = MilestoneAgeCurveParams(min_relevant_age_margin_months=6)
    expected_age, relevant_age_min, relevant_age_max = get_milestone_ages_from_curve(
        curve, params
    )
    assert relevant_age_min == 0
    assert relevant_age_max >= expected_age + 6
    assert relevant_age_max <= app_settings.MAX_CHILD_AGE_MONTHS


def test_stored_parameters_reconstruct_the_curve_exactly():
    """
    The stored parameters are the fitted parameters, so a curve rebuilt from them must
    be identical: the answers imputed when giving feedback for a child have to match
    those the statistics were built from.
    """
    fitted = fit_milestone_age_curve(counts_from_curve(15.3, 0.44))
    assert fitted.fit_ok
    reconstructed = MilestoneAgeCurve(
        midpoint=fitted.midpoint,
        steepness=fitted.steepness,
        n_answers=fitted.n_answers,
        fit_ok=True,
    )
    assert reconstructed == fitted
    for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
        assert reconstructed.mean_answer(age) == fitted.mean_answer(age)


def test_fit_is_robust_to_a_noisy_sparse_age():
    """A single age with few, unrepresentative answers must not drag the curve."""
    counts = counts_from_curve(30.0, 0.3)
    clean = fit_milestone_age_curve(counts)
    # two children of age 2 whose parents claim the milestone is fully achieved
    counts[2] = [0, 0, 0, 2]
    noisy = fit_milestone_age_curve(counts)
    assert noisy.fit_ok
    assert noisy.midpoint == pytest.approx(clean.midpoint, abs=1.0)
