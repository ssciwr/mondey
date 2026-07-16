# Algorithms

How MONDEY turns milestone answers into statistics and into feedback for parents.

## Answers

A parent answers each milestone on a four point scale, stored as `0`–`3`:

| Answer | Meaning |
| --- | --- |
| 0 | Noch gar nicht — not yet |
| 1 | In Ansätzen — first signs |
| 2 | Weitgehend — largely |
| 3 | Zuverlässig — reliably |

`-1` means the milestone was presented but not answered. An answer session containing a
`-1` is marked incomplete and takes no part in the statistics.

### Which milestones a child is asked

When an answer session is created
(`current_milestone_answer_session`), it contains the milestones that are:

- age relevant: `relevant_age_min <= child_age <= relevant_age_max`, using the values on
  the `milestone` table; and
- not already achieved: the child has not answered `3` for that milestone in any previous
  completed answer session;
- plus any milestones from the previous session that were answered below `3` but are no
  longer age relevant, so that these milestones are only skipped once the child has mastered it

So a milestone is absent from a session for one of these reasons:

| Why it is absent | What we know |
| --- | --- |
| The child has **already achieved** it | The answer is 3 — the child told us so in an earlier session |
| The child is **too young** to be asked | Nothing directly; the population is the best guide |
| The child is **too old** and was never asked | Nothing directly; the population is the best guide |
| The milestone **did not exist** when the session was answered | Nothing directly; the population is the best guide |

## The milestone age curve

The mean answer for a milestone is modelled as a
logistic function of the child's age in months:

```
mean_answer(age) = 3 / (1 + exp(-steepness * (age - midpoint)))
```

It rises monotonically from 0 (no child of that age shows the behaviour) to 3 (every child
does). `midpoint` is the age at which the mean answer is 1.5; `steepness` sets how quickly
the transition happens, so `1 / steepness` is the width of the transition in months.

### Fitting

The fit is a bounded, robust least squares fit (`scipy.optimize.least_squares`) of the
curve to the observed mean answer at each age

- Each residual is weighted by `sqrt(n)`, where `n` is the number
  of answers at that age, so an age with two answers cannot outweigh an age with fifty.
- A `soft_l1` loss stops a single unrepresentative age from dominating the fit.

### When the fit is rejected

`fit_ok` is `False` — and the fitted parameters are not used — if any of the following
hold:

| Condition | Why |
| --- | --- |
| Fewer than `MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT` answers (default 100, see `settings.py`) | Fitting a curve to a handful of answers would just be interpolating noise |
| Answers at fewer than two distinct ages | A transition cannot be located at all |
| The observed mean never crosses 1.5 (all above, or all below) | The transition is not bracketed by the data, so any number of curves fit equally well and the parameters would be arbitrary |
| `midpoint` lands on either bound (`0`, `MAX_CHILD_AGE_MONTHS`) | The transition is not contained in the supported age range |
| `steepness` lands on its lower bound (`0.01`) | The curve is flat, so there is no transition to locate |
| The optimiser fails to converge | — |

### Expected age and relevant age range

Given a fitted curve, the ages are read off it, as the ages at which the curve crosses a
given mean answer, then rounded to whole months and clamped to `[0, MAX_CHILD_AGE_MONTHS]`
(`get_milestone_ages_from_curve`):

| Quantity | Mean answer crossed | Parameter | Default |
| --- | --- | --- | --- |
| `relevant_age_min` | 0.3 | `mean_answer_relevant_min` | 0.3 |
| `expected_age` | 2.4 | `mean_answer_achieved` | 2.4 |
| `relevant_age_max` | 2.7 | `mean_answer_relevant_max` | 2.7 |

The three thresholds are admin-configurable. There is also an admin-configurable minimum margin,
so the final range is widened to cover at least `min_relevant_age_margin_months` either side
of the expected age:

```
relevant_age_min = min(relevant_age_min, expected_age - margin)
relevant_age_max = max(relevant_age_max, expected_age + margin)
```

## Which answer sessions count

The statistics (`async_update_stats`) are computed over answer sessions that are:

- `completed`, and not incomplete due to a `-1` answer (`flag_incomplete_answer_sessions`);
- not from a test account (email matching `%tester@testaccount.com`);
- not suspicious: `suspicious_state` is `not_suspicious` or `admin_not_suspicious`.

A session is flagged suspicious automatically (`flag_suspicious_answer_sessions`) if the
root mean square difference between its answers and the expected answers for the child's
age exceeds `1.0` (`analyse_answer_session`).

Admins can also manually mark answer sessions as suspicious or not
suspicious, which takes precedence over any automatic analysis.

## Milestone group statistics

A milestone group's statistics describe the distribution, over children of a given age, of
each child's average answer across the milestones in that group.

If a milestone has no answer because the child already answered 3 for it in a previous
answer session, we use 3 as their answer.

If a milestone has no answer because it was not asked, we impute `mean_answer(child_age)`
from the milestone's curve — the mean answer of children of this age.
This covers a child who was too young or too old to be asked, and a milestone that did not
exist when the session was answered.

Milestones **without** a fitted curve are excluded from the group average — for every
answer session, not just the ones missing them. Excluding them for everyone is what keeps
the group averages comparable between children: every child's score is an average over the
same set of milestones.

## Feedback

Feedback is a traffic light (`TrafficLight`): `1` green, `0` yellow, `-1` red, and `-2`
invalid, meaning there is not enough data to say anything.

### Milestone feedback (detailed)

Per milestone, for each answer in the session (`compute_feedback_milestone`):

| Condition | Feedback |
| --- | --- |
| The milestone does not exist | invalid (-2) |
| `child_age < milestone.expected_age_months` | green (1) — the child is not yet expected to have achieved it |
| answer is 0 | red (-1) |
| answer is 1 | yellow (0) |
| answer is 2 or 3 | green (1) |

### Milestone group feedback (summary)

Per milestone group (`compute_milestonegroup_feedback_summary`), the child's average score
for the group is computed the same way the group statistics are.

That score is then compared against the stored mean and standard deviation for that group
and child age (`compute_feedback_milestone_group`):

| Condition | Feedback |
| --- | --- |
| Fewer than 5 answer sessions in the statistics for this group and age | invalid (-2) |
| `score < mean - 2 * stddev` | red (-1) |
| `mean - 2 * stddev <= score < mean - stddev` | yellow (0) |
| `score >= mean - stddev` | green (1) |

## Adding a milestone

When a new milestone is added, initially there are no answers for it so it is simply
left out of group averages until it has enough answers
to fit a curve (`MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT`).

Once this is the case, and assuming the resulting fit is good enought to use,
the milestone is included in the group answers,
and any answer sessions that didn't include the milestone as it didn't exist then use
the imputed average score for a child of this age when calculating the average to compare.
