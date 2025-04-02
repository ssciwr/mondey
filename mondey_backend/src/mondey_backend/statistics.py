from __future__ import annotations

import datetime
import logging
from collections import defaultdict
from collections.abc import Sequence

import numpy as np
from sqlmodel import col
from sqlmodel import select

from mondey_backend.dependencies import SessionDep
from mondey_backend.dependencies import UserAsyncSessionDep
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestionText
from mondey_backend.models.users import User
from mondey_backend.routers.utils import _get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import _get_expected_age_from_scores
from mondey_backend.users import is_test_account_user


# see: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
# reason for not using existing package: bessel correction usually not respected
# we are using Welford's method here. This necessitates recording the count.
def _add_sample(
    count: int,
    mean: float,
    m2: float,
    new_value: float,
) -> tuple[int, float, float]:
    """
    Add a sample to the current statistics.
    This function uses an online algorithm to compute the mean (directly) and an intermediate for the variance.
    This uses Welford's method with a slight modification to avoid numerical instability.
    See https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm

    Parameters
    ----------
    count : int
        number of samples added so far.
    mean : float
        current mean of the samples.
    m2 : float
        intermediate value for the variance computation.
    new_value : float
        new sample to be added to the statistics.

    Returns
    -------
    tuple[int, float, float]
        updated count, mean, and m2 values.
    """
    count += 1
    delta = new_value - mean
    mean += delta / count
    delta2 = new_value - mean
    m2 += delta * delta2
    return count, mean, m2


def _finalize_statistics(
    count: int | np.ndarray,
    mean: float | np.ndarray,
    m2: float | np.ndarray,
) -> tuple[int | np.ndarray, float | np.ndarray, float | np.ndarray]:
    """
    Compute the mean and standard deviation from the intermediate values.
    This function is used to finalize the statistics after a batch of new samples have been added.
    If arrays are supplied, they all need to have the same shape.
    Values for the standard deviation for which the count is less than 2 are set to zero.

    Parameters
    ----------
    count : int | np.ndarray
        Current counts of samples. If ndarray, it contains the number of samples for each entry.
    mean : float | np.ndarray
        Current mean value of the samples. If ndarray, it contains the mean for each entry.
    m2 : float | np.ndarray
        Current intermediate value for variance computation. If ndarray, it contains the intermediate value for each entry.

    Returns
    -------
    tuple[int | np.ndarray, float | np.ndarray, float | np.ndarray]
        updated count, mean, and standard deviation values.

    Raises
    ------
    ValueError
        If arguments of incompatible types are given

    ValueError
        If arrays have different shapes.
    """
    if all(isinstance(x, float | int) for x in [count, mean, m2]):
        if count < 2:
            return count, mean, 0.0
        else:
            var = m2 / (count - 1)
            return count, mean, np.sqrt(var)
    elif (
        isinstance(count, np.ndarray)
        and isinstance(mean, np.ndarray)
        and isinstance(m2, np.ndarray)
    ):
        if count.shape != m2.shape or mean.shape != m2.shape:
            raise ValueError(
                "Given arrays for statistics computation must have the same shape."
            )

        with np.errstate(invalid="ignore"):
            valid_counts = count >= 2
            variance = m2
            variance[valid_counts] /= count[valid_counts] - 1
            variance[np.invert(valid_counts)] = 0.0
            return (
                count,
                np.nan_to_num(mean),
                np.nan_to_num(np.sqrt(variance)),
            )  # get stddev
    else:
        raise ValueError(
            "Given values for statistics computation must be of type int|float|np.ndarray"
        )


def _get_statistics_by_age(
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    count: np.ndarray | None = None,
    avg: np.ndarray | None = None,
    stddev: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate mean and variance for a set of answers by age in months. Makes use of an online
    algorithm for variance and mean calculation that updates preexisting statistics with the
    values provided in the answers.

    Parameters
    ----------
    answers : Sequence[MilestoneAnswer]
        Answers to include in the statistics.
    child_ages : dict[int, int]
        Dictionary of answer_session_id -> age in months.
    count : np.ndarray | None, optional
        Number of elements from which the current statistics is built, by default None.
        Will be initialized as a zero array if None.
    avg : np.ndarray | None, optional
        Current mean values per age, by default None.
        Will be initialized as a zero array if None.
    stddev : np.ndarray | None, optional
        Current standard deviation values per age, by default None.
        Will be initialized as a zero array if None.
    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Updated count, avg and stddev arrays.
    """
    if count is None or avg is None or stddev is None:
        max_age_months = 100
        count = np.zeros(max_age_months + 1, dtype=np.int32)
        avg = np.zeros(max_age_months + 1, dtype=np.float64)
        stddev = np.zeros(max_age_months + 1, dtype=np.float64)

    if child_ages == {}:
        return count, avg, stddev

    # online algorithm computes variance, compute m2 from stddev
    # we can ignore count-1 <= 0 because stddev is zero in this case
    m2 = np.pow(stddev, 2) * (count - 1)

    for answer in answers:
        age = child_ages[answer.answer_session_id]  # type: ignore
        new_count, new_avg, new_m2 = _add_sample(
            count[age], avg[age], m2[age], answer.answer + 1
        )
        count[age] = new_count
        avg[age] = new_avg
        m2[age] = new_m2

    count, avg, stddev = _finalize_statistics(count, avg, m2)

    return count, avg, stddev


async def get_test_account_user_ids(user_session: UserAsyncSessionDep) -> list[int]:
    """
    Lists user IDs that are identified as test accounts
    """
    users = await user_session.execute(select(User))
    users_as_list = (
        users.scalars().all()
    )  # IIRC this converts to python list object from Cursor.
    test_user_ids = [user.id for user in users_as_list if is_test_account_user(user)]
    return test_user_ids


def make_any_stale_answer_sessions_inactive(
    session: SessionDep, test_account_user_ids_to_exclude: list[int]
) -> None:
    """
    mark any answersession that is older than 9 days as inactive by setting the expired flag. Delete any older than 9 days which are test account answersessions.
    This includes a grace period of 2 days wrt the normal expiration timedelta of 7 days to avoid setting currently in-use answersessions to expired.
    """
    days_after_which_session_is_stale = 9
    stale_date = datetime.datetime.now() - datetime.timedelta(
        days=days_after_which_session_is_stale
    )
    for stale_milestone_answer_session in session.exec(
        select(MilestoneAnswerSession)
        .where(~col(MilestoneAnswerSession.expired))
        .where(col(MilestoneAnswerSession.created_at) <= stale_date)
    ).all():
        # Now, if it is a test account one, delete it rather than set it to expired? It will cascade to the milestone_answers?
        # Can we soft-delete it, have a "deleted" variable instead?
        if (
            stale_milestone_answer_session.user_id in test_account_user_ids_to_exclude
            and stale_milestone_answer_session.user_id is not None
        ):
            # Below is dangerous as it deletes data.
            session.delete(stale_milestone_answer_session)
        else:
            stale_milestone_answer_session.expired = True
            session.add(stale_milestone_answer_session)
    session.commit()


async def async_update_stats(
    session: SessionDep,
    user_session: UserAsyncSessionDep,
    incremental_update: bool = True,
):
    """Update the recorded statistics of the milestonegroups and milestones.
    It only uses expired milestoneanswersesssions. If `incremental_update` is True, it will only update the current statistics wit the new answersessions. Else, it will recalculate all statistics completely. The latter may be necessary if admins change the answersessions in the database by hand.
    Args:
        session (SessionDep): database session
        incremental_update (bool, optional): Whether or not to recalculate the statistics completely. Defaults to True.

    Returns:
        str: Message string indicating successful statistics calculation or update
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Starting {'incremental' if incremental_update else 'full'} statistics update"
    )

    # We gather these first then exclude later so that we don't do a FK join on the user_id<->email for stale+filtering
    test_account_user_ids_to_exclude = await get_test_account_user_ids(user_session)
    make_any_stale_answer_sessions_inactive(session, test_account_user_ids_to_exclude)

    # get MilestoneAnswerSessions to be used for calculating statistics
    answer_session_filter = (
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.expired))
        .where(
            col(MilestoneAnswerSession.user_id).not_in(test_account_user_ids_to_exclude)
        )
    )
    if incremental_update:
        answer_session_filter = answer_session_filter.where(
            ~col(MilestoneAnswerSession.included_in_statistics)
        )
    milestone_answer_sessions = session.exec(answer_session_filter).all()

    child_ages = _get_answer_session_child_ages_in_months(
        session, milestone_answer_sessions
    )
    logger.debug(f"  - found {len(milestone_answer_sessions)} answer sessions")

    # construct a list of MilestoneAnswers for each Milestone and MilestoneGroup
    milestone_answers: dict[int, list[MilestoneAnswer]] = defaultdict(list)
    milestone_group_answers: dict[int, list[MilestoneAnswer]] = defaultdict(list)
    for milestone_answer_session in milestone_answer_sessions:
        for milestone_id, answer in milestone_answer_session.answers.items():
            milestone_answers[milestone_id].append(answer)
            milestone_group_answers[answer.milestone_group_id].append(answer)

    # update milestone statistics
    logger.debug(f"  - updating {len(milestone_answers)} milestone statistics...")
    for milestone_id, answers in milestone_answers.items():
        existing_milestone_statistics = (
            session.get(MilestoneAgeScoreCollection, milestone_id)
            if incremental_update
            else None
        )
        milestone_age_score_collection = calculate_milestone_statistics_by_age(
            milestone_id, answers, child_ages, existing_milestone_statistics
        )
        session.merge(milestone_age_score_collection)

    # update milestone group statistics
    logger.debug(
        f"  - updating {len(milestone_group_answers)} milestone group statistics..."
    )
    for milestone_group_id, answers in milestone_group_answers.items():
        existing_milestone_group_statistics = (
            session.get(MilestoneGroupAgeScoreCollection, milestone_group_id)
            if incremental_update
            else None
        )
        milestone_group_age_score_collection = (
            calculate_milestonegroup_statistics_by_age(
                milestone_group_id,
                answers,
                child_ages,
                existing_milestone_group_statistics,
            )
        )
        session.merge(milestone_group_age_score_collection)

    for milestone_answer_session in milestone_answer_sessions:
        milestone_answer_session.included_in_statistics = True
        session.add(milestone_answer_session)

    session.commit()
    logger.debug("  - done")
    return f"{'Incremental' if incremental_update else 'Full'} statistics update complete using {len(milestone_answer_sessions)} answer sessions."


def _extract_stats(
    existing_statistics: MilestoneGroupAgeScoreCollection
    | MilestoneAgeScoreCollection
    | None,
) -> tuple[np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    """
    Extract count, avg and stddev arrays from an AgeScoreCollection

    Parameters
    ----------
    existing_statistics : MilestoneGroupAgeScoreCollection | MilestoneAgeScoreCollection | None
        The collection to extract statistics from.
    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        count, avg and stddev arrays.
    """
    if existing_statistics is None:
        return None, None, None

    last_scores = existing_statistics.scores
    count = np.array([score.count for score in last_scores], dtype=np.int32)
    avg_scores = np.array([score.avg_score for score in last_scores], dtype=np.float64)
    stddev_scores = np.array(
        [score.stddev_score for score in last_scores], dtype=np.float64
    )
    return count, avg_scores, stddev_scores


def calculate_milestone_statistics_by_age(
    milestone_id: int,
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    existing_statistics: MilestoneAgeScoreCollection | None,
) -> MilestoneAgeScoreCollection | None:
    """
    Calculate the mean, variance of a milestone per age in months.
    If existing statistics are provided they are updated using the provided answers.

    Parameters
    ----------
    milestone_id : int
        id of the milestone to calculate the statistics for
    answers: Sequence[MilestoneAnswer]
        the new answers to include in the statistics.
    child_ages : dict[int, int]
        dict of answer_session_id -> child age in months
    existing_statistics: MilestoneAgeScoreCollection | None
        the existing statistics to update, if any
    Returns
    -------
    MilestoneAgeScoreCollection | None
        updated statistics, or None if there are no new answers and no existing statistics.
    """
    if len(answers) == 0:
        # return existing statistics if no new answers are available
        return existing_statistics

    # initialize avg and stddev scores with the existing statistics or to None if no statistics are available
    count, avg_scores, stddev_scores = _extract_stats(existing_statistics)

    count, avg_scores, stddev_scores = _get_statistics_by_age(
        answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
    )

    expected_age = _get_expected_age_from_scores(avg_scores)

    # overwrite last_statistics with updated stuff --> set primary keys explicitly
    return MilestoneAgeScoreCollection(
        milestone_id=milestone_id,
        expected_age=expected_age,
        created_at=datetime.datetime.now(),
        scores=[
            MilestoneAgeScore(
                age=age,
                milestone_id=milestone_id,
                count=int(
                    count[age]
                ),  # need a conversion to avoid numpy.int32 being stored as byte object
                avg_score=avg_scores[age],
                stddev_score=stddev_scores[age],
                expected_score=4 if age >= expected_age else 1,
            )
            for age in range(0, len(avg_scores))
        ],
    )


def calculate_milestonegroup_statistics_by_age(
    milestone_group_id: int,
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    existing_statistics: MilestoneGroupAgeScoreCollection | None,
) -> MilestoneGroupAgeScoreCollection | None:
    """
    Calculate the mean, variance of a milestone group per age in months.
    If existing statistics are provided they are updated using the provided answers.

    Parameters
    ----------
    milestone_group_id : int
        id of the milestone group to calculate the statistics for
    answers: Sequence[MilestoneAnswer]
        the new answers to include in the statistics.
    child_ages : dict[int, int]
        dict of answer_session_id -> child age in months
    existing_statistics: MilestoneGroupAgeScoreCollection | None
        the existing statistics to update, if any
    Returns
    -------
    MilestoneGroupAgeScoreCollection | None
        updated statistics, or None if there are no new answers and no existing statistics.
    """
    if len(answers) == 0:
        # return existing statistics if no new answers are available
        return existing_statistics

    # initialize avg and stddev scores with the existing statistics or to None if no statistics are available
    count, avg_scores, stddev_scores = _extract_stats(existing_statistics)
    count, avg_scores, stddev_scores = _get_statistics_by_age(
        answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
    )

    return MilestoneGroupAgeScoreCollection(
        milestone_group_id=milestone_group_id,
        scores=[
            MilestoneGroupAgeScore(
                milestone_group_id=milestone_group_id,
                age=age,
                count=int(
                    count[age]
                ),  # need a conversion to avoid numpy.int32 being stored as byte object
                avg_score=avg_scores[age],
                stddev_score=stddev_scores[age],
            )
            for age in range(0, len(avg_scores))
        ],
        created_at=datetime.datetime.now(),
    )


async def get_user_ids(
    user_session: UserAsyncSessionDep, research_group_id: int
) -> list[int]:
    users = await user_session.execute(
        select(User).where(col(User.research_group_id) == research_group_id)
    )
    return [user.id for user in users.scalars().all()]


def make_datatable(
    milestone_answer_sessions: Sequence[MilestoneAnswerSession],
    user_answers: dict[int, dict[str, str | int | float]],
    child_answers: dict[int, dict[str, str | int | float]],
    child_ages: dict[int, int],
) -> list[dict[str, str | int | float]]:
    datatable: list[dict[str, str | int | float]] = []
    for milestone_answer_session in milestone_answer_sessions:
        if milestone_answer_session.id in child_ages:
            for milestone_id, answer in milestone_answer_session.answers.items():
                row: dict[str, str | int | float] = (
                    {
                        "milestone_group_id": answer.milestone_group_id,
                        "milestone_id": milestone_id,
                        "answer": answer.answer + 1,
                        "child_age": child_ages[milestone_answer_session.id],  # type: ignore
                        "answer_session_id": milestone_answer_session.id,
                    }
                    | user_answers[milestone_answer_session.user_id]
                    | child_answers[milestone_answer_session.child_id]
                )
                datatable.append(row)
    return datatable


def get_user_answers(session: SessionDep) -> dict[int, dict[str, str | int | float]]:
    questions = {
        q.user_question_id: q.question
        for q in session.exec(
            select(UserQuestionText).where(col(UserQuestionText.lang_id) == "de")
        ).all()
    }
    user_answers: dict[int, dict[str, str | int | float]] = defaultdict(dict)
    for answer in session.exec(select(UserAnswer)).all():
        user_answers[answer.user_id][questions[answer.question_id]] = answer.answer
    return user_answers


def get_child_answers(session: SessionDep) -> dict[int, dict[str, str | int | float]]:
    questions = {
        q.child_question_id: q.question
        for q in session.exec(
            select(ChildQuestionText).where(col(ChildQuestionText.lang_id) == "de")
        ).all()
    }
    child_answers: dict[int, dict[str, str | int | float]] = defaultdict(dict)
    for answer in session.exec(select(ChildAnswer)).all():
        child_answers[answer.child_id][questions[answer.question_id]] = answer.answer
    return child_answers


async def extract_research_data(
    session: SessionDep,
    user_session: UserAsyncSessionDep,
    research_group_id: int | None = None,
) -> list[dict[str, str | int | float]]:
    user_ids_to_exclude = await get_test_account_user_ids(user_session)
    answer_session_filter = select(MilestoneAnswerSession).where(
        col(MilestoneAnswerSession.user_id).not_in(user_ids_to_exclude)
    )
    if research_group_id is not None:
        user_ids = await get_user_ids(user_session, research_group_id)
        answer_session_filter = answer_session_filter.where(
            col(MilestoneAnswerSession.user_id).in_(user_ids)
        )
    milestone_answer_sessions = session.exec(answer_session_filter).all()
    child_ages = _get_answer_session_child_ages_in_months(
        session, milestone_answer_sessions
    )
    user_answers = get_user_answers(session)
    child_answers = get_child_answers(session)
    return make_datatable(
        milestone_answer_sessions, user_answers, child_answers, child_ages
    )
