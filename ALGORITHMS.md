# Algorithms

How MONDEY turns milestone answers into statistics and into feedback for parents.

This document describes what the code actually does. The relevant source is:

| What | Where |
| --- | --- |
| Age curve fit, expected age, relevant age range | `mondey_backend/src/mondey_backend/routers/utils.py` |
| Statistics update (milestones and milestone groups) | `mondey_backend/src/mondey_backend/statistics.py` |
| Feedback (traffic lights) | `mondey_backend/src/mondey_backend/routers/scores.py` |
| Stored statistics | `mondey_backend/src/mondey_backend/models/milestones.py` |

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

This matters for everything below, because it is what makes a *missing* answer informative
rather than merely absent. When an answer session is created
(`current_milestone_answer_session`), it contains the milestones that are:

- age relevant: `relevant_age_min <= child_age <= relevant_age_max`, using the values on
  the `milestone` table; and
- not already achieved: the child has not answered `3` for that milestone in any previous
  completed answer session;
- plus any milestone from the previous session that was answered below `3` but is no
  longer age relevant, so a child is not dropped mid-milestone.

Note that an already achieved milestone is **omitted** from the session — no answer is
recorded for it at all, not even a copy of the previous `3`.

So a milestone is absent from a session for one of these reasons, and they are **not**
equivalent:

| Why it is absent | What we know |
| --- | --- |
| The child has **already achieved** it | The answer is 3 — the child told us so in an earlier session |
| The child is **too young** to be asked | Nothing directly; the population is the best guide |
| The child is **too old** and was never asked | Nothing directly; the population is the best guide |
| The milestone **did not exist** when the session was answered | Nothing directly; the population is the best guide |

This distinction matters, and is handled explicitly when averaging over a group: see
"Milestone group statistics".

## The milestone age curve

Everything a milestone's statistics say about age comes from one fitted curve
(`fit_milestone_age_curve`). This is deliberate: the expected age, the relevant age range,
and the value imputed for a missing answer are all derived from the same fit, so they
cannot drift apart.

The mean answer for a milestone is modelled as a logistic function of the child's age in
months:

```
mean_answer(age) = 3 / (1 + exp(-steepness * (age - midpoint)))
```

It rises monotonically from 0 (no child of that age shows the behaviour) to 3 (every child
does). `midpoint` is the age at which the mean answer is 1.5; `steepness` sets how quickly
the transition happens, so `1 / steepness` is the width of the transition in months.

### Fitting

The fit is a bounded, robust least squares fit (`scipy.optimize.least_squares`) of the
curve to the observed mean answer at each age, where the observed mean at an age comes from
the answer counts `c0`–`c3` for that age:

```
observed_mean(age) = (c1 + 2*c2 + 3*c3) / (c0 + c1 + c2 + c3)
```

Three properties matter:

- **Weighted by evidence.** Each residual is weighted by `sqrt(n)`, where `n` is the number
  of answers at that age, so an age with two answers cannot outweigh an age with fifty.
- **Robust.** A `soft_l1` loss stops a single unrepresentative age from dominating the fit.
- **Gaps are free.** An age with no answers simply carries no weight, which is what lets the
  curve interpolate over gaps and extrapolate past the ends of the observed data.

The curve is parametrised by `expected_age` rather than by `midpoint`, so the quantity that
is reported and stored is itself a fitted parameter rather than something derived after the
fact.

### When the fit is rejected

`fit_ok` is `False` — and the fitted parameters must not be used — if any of the following
hold:

| Condition | Why |
| --- | --- |
| Fewer than `MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT` answers (default 100, see `settings.py`) | Fitting a curve to a handful of answers would just be interpolating noise |
| Answers at fewer than two distinct ages | A transition cannot be located at all |
| The observed mean never crosses 1.5 (all above, or all below) | The transition is not bracketed by the data, so any number of curves fit equally well and the parameters would be arbitrary |
| `steepness` lands on either bound (`0.01`, `2.0`) | The transition is either not contained in the observed age range, or sharper than the data can resolve |
| The optimiser fails to converge | — |

This is what makes a **newly added milestone** safe. No existing answer session contains it,
so it has few answers, so no curve is fitted, so it is left out of the group statistics
entirely until enough answers accumulate. It then joins automatically on a later statistics
update. See "Adding a milestone" below.

### Expected age and relevant age range

Given a fitted curve, the ages are read off it, as the ages at which the curve crosses a
given mean answer, then rounded to whole months and clamped to `[0, MAX_CHILD_AGE_MONTHS]`
(`get_milestone_ages_from_curve`):

| Quantity | Mean answer crossed | Constant |
| --- | --- | --- |
| `relevant_age_min` | 0.3 | `MEAN_ANSWER_RELEVANT_MIN` |
| `expected_age` | 2.4 | `MEAN_ANSWER_ACHIEVED` |
| `relevant_age_max` | 2.7 | `MEAN_ANSWER_RELEVANT_MAX` |

`MEAN_ANSWER_ACHIEVED = 2.4` is 80% of the maximum answer of 3, which is what the previous
"at least 80% of children have achieved it" rule meant. The relevant range therefore runs
from when a few children show the behaviour until nearly all of them do, and its width is
set by the fitted `steepness`: a milestone with a sharp transition gets a narrow range, one
with a gradual transition gets a wide one.

**Fallback.** If the fit was rejected, these three values fall back to the previous
heuristics (`_get_expected_age_from_scores_heuristic` and
`_get_relevant_age_min_max_heuristic`): the expected age is the youngest age at which at
least 80% of at least three answers were 2 or 3, defaulting to `MAX_CHILD_AGE_MONTHS` if
there is no such age. These heuristics are noise sensitive — a single child at a young age
can set the expected age — which is why the fit replaced them, but they still give a value
where no curve can be fitted.

**These values are advisory.** They are stored on `milestoneagescorecollection`, which is
derived data. They only affect what the questionnaire asks once an admin applies them to the
`milestone` table from the admin interface, which plots the fitted curve over the observed
means so it can be checked first.

## Which answer sessions count

The statistics (`async_update_stats`) are computed over answer sessions that are:

- `completed`, and not incomplete due to a `-1` answer (`flag_incomplete_answer_sessions`);
- not from a test account (email matching `%tester@testaccount.com`);
- not suspicious: `suspicious_state` is `not_suspicious` or `admin_not_suspicious`.

A session is flagged suspicious automatically (`flag_suspicious_answer_sessions`) if the
root mean square difference between its answers and the expected answers for the child's
age exceeds `1.0` (`analyse_answer_session`). Only sessions with an `unknown` state are
flagged, so an admin's manual decision is never overwritten. Sessions used are marked
`included_in_statistics`.

The expected answer for a milestone comes from its fitted age curve, which is defined at
every age. If it has no usable curve, the mean answer observed at exactly that age is used
instead; and if no child of that age has answered that milestone, there is nothing to
compare against and it is left out of the comparison. That last case matters: treating it
as an expected answer of 0 would make the first child of their age to be asked about a
milestone look suspicious simply for having achieved it.

This uses the curves fitted by the *previous* statistics update, since which sessions are
suspicious is what determines which sessions this update fits its curves from.

## Milestone statistics

For each milestone and each child age in months, `milestoneagescore` stores the counts
`c0`–`c3` of each answer. **Only answers that were actually given are counted** — no
imputation happens here, so a milestone's own statistics are unaffected by it. The
per-milestone mean and sample standard deviation are computed from those counts
(`MilestoneAgeScore.mean` / `.stddev`).

## Milestone group statistics

A milestone group's statistics describe the distribution, over children of a given age, of
each child's *average answer across the milestones in that group*. `async_update_stats`
computes them in two passes, because the imputed values needed in the second pass depend on
the curves fitted from the first:

1. **Count** the answers per milestone and age, as above, and fit each milestone's age curve.
2. **Average** over the milestones in each group, for each answer session, to get one score
   per session.

In the second pass, for each milestone in the group **that has a fitted curve**:

- if the session has an answer, use it;
- else if the child **already achieved** the milestone — they answered 3 for it in an
  earlier completed session, which is why it is no longer being asked — use **3**. This is
  not an imputation: we know the answer. Imputing here would understate the child, and would
  understate them the most the *earlier* they achieved it, since that is when the population
  mean is lowest;
- otherwise impute `mean_answer(child_age)` from the milestone's curve — the mean answer of
  children of this age. This covers a child who is too young to be asked, one who is past
  the range and was never asked, and a milestone that did not exist when the session was
  answered.

Milestones **without** a fitted curve are excluded from the group average — for every
answer session, not just the ones missing them. Excluding them for everyone is what keeps
the group averages comparable between children: every child's score is an average over the
same set of milestones.

Each session's group average then contributes to `count`, `sum_score` and
`sum_squaredscore` for that group and age, from which the group mean and sample standard
deviation are recovered. If no milestone in a group has a usable curve, the group's
statistics are left empty.

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

Note this uses `expected_age_months` from the `milestone` table — the value an admin has
applied — not the freshly computed one.

### Milestone group feedback (summary)

Per milestone group (`compute_milestonegroup_feedback_summary`), the child's average score
for the group is computed **the same way the group statistics are** — over the milestones
with a fitted curve, scoring an already achieved milestone as 3 and otherwise imputing the
curve for any that the session does not contain. This matching matters: a score computed
differently from the reference it is compared against would not be meaningful.

That score is then compared against the stored mean and standard deviation for that group
and child age (`compute_feedback_milestone_group`):

| Condition | Feedback |
| --- | --- |
| Fewer than 5 answer sessions in the statistics for this group and age | invalid (-2) |
| `score < mean - 2 * stddev` | red (-1) |
| `mean - 2 * stddev <= score < mean - stddev` | yellow (0) |
| `score >= mean - stddev` | green (1) |

Feedback is only reported for a group that the answer session has at least one answer for.
If such a group has no milestone with a usable curve, it is reported as invalid rather than
omitted.

## Adding a milestone

Adding a milestone to a group changes what that group's average is taken over, so it is
worth being explicit about what happens.

No existing answer session contains the new milestone. Imputing a value for it in those
sessions would bias the group statistics: the imputation assumes a milestone is missing
because of the child's age, but a new milestone is missing because it did not exist yet.
Instead the milestone is simply left out of the group average until it has enough answers
to fit a curve (`MILESTONE_MIN_ANSWERS_FOR_CURVE_FIT`), and joins on a later statistics
update. Its own per-milestone statistics are unaffected throughout, since those only ever
count real answers.

The group's historical baseline does shift when a milestone crosses that threshold and
joins the average. This is expected: the statistics are recomputed wholesale on each update,
so the reference and the scores compared against it always come from the same milestone set.

## Known limitations

- **Imputation shrinks variance.** Imputing the mean answer for a missing milestone reduces
  the spread of group scores between children, so the reference standard deviation is
  narrower than it would be if every milestone were answered. Since group feedback is
  defined in units of that standard deviation, this makes it somewhat more sensitive.
- **The logistic assumes a monotonic transition.** A milestone whose mean answer does not
  rise steadily with age is not described well by the curve. In practice the fit is rejected
  when the data does not support it, rather than fitting something misleading.
- **Milestones that transition outside the observed age range** — at the very youngest ages,
  or beyond `MAX_CHILD_AGE_MONTHS` — cannot be fitted, and fall back to the heuristics.
