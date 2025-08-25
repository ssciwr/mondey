from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Sequence

import numpy as np
import pandas as pd
from sqlalchemy import update
from sqlmodel import col
from sqlmodel import func
from sqlmodel import select

from mondey_backend.dependencies import SessionDep
from mondey_backend.dependencies import UserAsyncSessionDep
from mondey_backend.logging import logger
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerAnalysis
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneAnswerSessionAnalysis
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.users import User
from mondey_backend.routers.utils import get_answer_session_child_ages_in_months
from mondey_backend.routers.utils import get_child_age_in_months
from mondey_backend.routers.utils import get_expected_age_from_scores
from mondey_backend.routers.utils import get_relevant_age_min_max
from mondey_backend.settings import app_settings


async def get_test_account_user_ids(user_session: UserAsyncSessionDep) -> list[int]:
    """
    Lists user IDs that are identified as test accounts
    """
    res = await user_session.execute(
        select(User.id).where(col(User.email).like("%tester@testaccount.com"))
    )
    return list(res.scalars().all())


def analyse_answer_session(
    session: SessionDep, milestone_answer_session: MilestoneAnswerSession
) -> MilestoneAnswerSessionAnalysis:
    analysis = MilestoneAnswerSessionAnalysis(rms=0, child_age=0, answers=[])
    child = session.get(Child, milestone_answer_session.child_id)
    if child is None:
        logger.error(f"Child {milestone_answer_session.child_id} does not exist")
        return analysis
    child_age = get_child_age_in_months(child, milestone_answer_session.created_at)
    if child_age > app_settings.MAX_CHILD_AGE_MONTHS:
        logger.warning(
            f"Child {child.id} has age {child_age} which is older than {app_settings.MAX_CHILD_AGE_MONTHS} months, skipping analysis"
        )
        return analysis
    analysis.child_age = child_age
    logger.debug(
        f"  - checking answer session {milestone_answer_session.id}, child age {child_age}"
    )
    diff = 0
    count = 0
    for milestone_id, answer in milestone_answer_session.answers.items():
        if answer.answer < 0:
            logger.debug(
                f"    - no answer available for milestone {milestone_id} - skipping"
            )
            continue
        score = session.get(
            MilestoneAgeScore, {"age": child_age, "milestone_id": milestone_id}
        )
        if score is None:
            logger.warning(
                f"    - no statistics available for milestone {milestone_id} - skipping"
            )
            continue
        analysis.answers.append(
            MilestoneAnswerAnalysis(
                milestone_id=milestone_id,
                answer=answer.answer,
                avg_answer=score.mean,
                stddev_answer=score.stddev,
            )
        )
        diff += np.power(score.mean - answer.answer, 2)
        count += 1
    if count == 0:
        analysis.rms = 0
    else:
        analysis.rms = np.sqrt(diff / count)
    logger.debug(f"    rms {analysis.rms}")
    return analysis


def flag_incomplete_answer_sessions(session: SessionDep):
    """
    Check for any answer sessions that are marked `completed` but have `-1` as an answer for any milestone,
    and set `complete` to `False` for those sessions.
    """
    answer_session_ids = set(
        session.exec(
            select(MilestoneAnswer.answer_session_id).where(
                col(MilestoneAnswer.answer) < 0
            )
        ).all()
    )
    for milestone_answer_session in session.exec(
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.completed))
        .where(col(MilestoneAnswerSession.id).in_(answer_session_ids))
    ).all():
        logger.warning(
            f"Answer session {milestone_answer_session.id} was marked completed but has missing answers, marking as incomplete"
        )
        milestone_answer_session.completed = False
    session.commit()


def flag_suspicious_answer_sessions(
    session: SessionDep,
    test_account_user_ids_to_exclude: list[int],
    threshold: float = 1.0,
):
    """
    Flag any new answer sessions with rms difference to average answers for that age greater than `threshold` as suspicious.
    Only updates sessions that with unknown SuspiciousState (i.e. that haven't been analysed or manually tagged by an admin).
    """
    milestone_answer_sessions = session.exec(
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.completed))
        .where(col(MilestoneAnswerSession.suspicious_state) == SuspiciousState.unknown)
        .where(
            col(MilestoneAnswerSession.user_id).not_in(test_account_user_ids_to_exclude)
        )
    ).all()
    logger.debug(
        f"  - found {len(milestone_answer_sessions)} answer sessions to check for suspiciousness"
    )
    for milestone_answer_session in milestone_answer_sessions:
        try:
            analysis = analyse_answer_session(session, milestone_answer_session)
            state = (
                SuspiciousState.suspicious
                if analysis.rms > threshold
                else SuspiciousState.not_suspicious
            )
            logger.debug(
                f"Marking answer session {milestone_answer_session.id} with rms difference {analysis.rms} as {'not' if state == SuspiciousState.not_suspicious else ''} suspicious"
            )
            milestone_answer_session.suspicious_state = state
        except AttributeError as e:
            logger.exception(e)


async def async_update_stats(
    session: SessionDep,
    user_session: UserAsyncSessionDep,
):
    """Update the recorded statistics of the milestonegroups and milestones.
    It only uses completed milestoneanswersesssions, excluding those from test users or those that are marked as suspicious.
    Args:
        session (SessionDep): database session
        user_session (UserAsyncSessionDep): user session

    Returns:
        str: Message string indicating successful statistics update
    """
    start_time = time.monotonic()
    logger.info("Starting statistics update")

    logger.info("  - flagging incomplete answer sessions")
    flag_incomplete_answer_sessions(session)

    # We gather these first then exclude later so that we don't do a FK join on the user_id<->email for stale+filtering
    test_account_user_ids_to_exclude = await get_test_account_user_ids(user_session)

    logger.info("  - flagging suspicious answer sessions")
    flag_suspicious_answer_sessions(session, test_account_user_ids_to_exclude)

    for answer_session in session.exec(select(MilestoneAnswerSession)).all():
        answer_session.included_in_statistics = False

    logger.info("  - collecting answer sessions")
    # get MilestoneAnswerSessions to be used for calculating statistics
    # filter to keep only those that are not test accounts and are explicitly marked as not suspicious (either by system or admin)
    answer_session_filter = (
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.completed))
        .where(
            col(MilestoneAnswerSession.user_id).not_in(test_account_user_ids_to_exclude)
        )
        .where(
            (
                col(MilestoneAnswerSession.suspicious_state)
                == SuspiciousState.not_suspicious
            )
            | (
                col(MilestoneAnswerSession.suspicious_state)
                == SuspiciousState.admin_not_suspicious
            )
        )
    )

    milestone_answer_sessions = session.exec(answer_session_filter).all()

    child_ages = get_answer_session_child_ages_in_months(
        session, milestone_answer_sessions
    )
    logger.info(
        f"  - calculating statistics using {len(milestone_answer_sessions)} answer sessions"
    )
    # array of values to store answer counts for each milestone and child age:
    max_milestone_id = session.exec(select(func.max(col(Milestone.id)))).one_or_none()
    if max_milestone_id is None:
        logger.info("No milestones found, skipping statistics update")
        return "No milestones found, skipping statistics update"
    m_counts = np.zeros(
        (max_milestone_id + 1, app_settings.MAX_CHILD_AGE_MONTHS + 1, 4),
        dtype=np.uint64,
    )
    # arrays of values to store counts, sum of scores and sum of scores squared for each milestone group & age:
    max_milestone_group_id = session.exec(
        select(func.max(col(MilestoneGroup.id)))
    ).one_or_none()
    if max_milestone_group_id is None:
        logger.info("No milestone groups found, skipping statistics update")
        return "No milestone groups found, skipping statistics update"
    mg_shape = (max_milestone_group_id + 1, app_settings.MAX_CHILD_AGE_MONTHS + 1)
    mg_counts = np.zeros(mg_shape, dtype=np.uint64)
    mg_sum_scores = np.zeros(mg_shape, dtype=np.float64)
    mg_sum_squaredscores = np.zeros(mg_shape, dtype=np.float64)

    milestones = session.exec(select(Milestone)).all()
    milestone_group_ids = session.exec(select(MilestoneGroup.id)).all()

    for milestone_answer_session in milestone_answer_sessions:
        child_age = child_ages[milestone_answer_session.id]  # type: ignore
        if 0 <= child_age <= app_settings.MAX_CHILD_AGE_MONTHS:
            logger.debug(
                f"    - answer session={milestone_answer_session.id} child_age={child_age}"
            )
            mg_local_count = np.zeros(max_milestone_group_id + 1)
            mg_local_sum = np.zeros(max_milestone_group_id + 1)
            for milestone in milestones:
                answer = milestone_answer_session.answers.get(milestone.id)  # type: ignore
                # if there is an answer for this milestone, include it in the statistics
                if answer is not None:
                    m_counts[milestone.id][child_age][answer.answer] += 1
                # whether or not there is an answer, we still need a value when calculating
                # the average and std dev of answers for the milestone group.
                # if the answer is missing, we assume a full score if the child is old enough to be asked about the milestone,
                # (since once the child achieves a milestone it is no longer asked in future sessions),
                # and a zero score if child is too young to be asked about this milestone.
                imputed_answer = 3 if child_age >= milestone.relevant_age_min else 0
                answer_value = answer.answer if answer is not None else imputed_answer
                if answer is None:
                    logger.debug(
                        f"    - milestone_group_id={milestone.group_id} milestone_id={milestone.id} imputed_answer={answer_value}"
                    )
                mg_local_count[milestone.group_id] += 1
                mg_local_sum[milestone.group_id] += answer_value
            for milestone_group_id in milestone_group_ids:
                mg_avg_score = (
                    mg_local_sum[milestone_group_id]
                    / mg_local_count[milestone_group_id]
                )
                logger.debug(
                    f"    - milestone group {milestone_group_id}: avg score {mg_avg_score}"
                )
                mg_counts[milestone_group_id][child_age] += 1
                mg_sum_scores[milestone_group_id][child_age] += mg_avg_score
                mg_sum_squaredscores[milestone_group_id][child_age] += np.pow(
                    mg_avg_score, 2
                )
            milestone_answer_session.included_in_statistics = True

    # save statistics
    logger.info("  - saving milestone statistics")
    for milestone in milestones:
        save_milestone_statistics(session, milestone.id, m_counts[milestone.id])  # type: ignore
    logger.info("  - saving milestone group statistics")
    for milestone_group_id in session.exec(select(MilestoneGroup.id)).all():
        save_milestone_group_statistics(
            session,
            milestone_group_id,  # type: ignore
            mg_counts[milestone_group_id],
            mg_sum_scores[milestone_group_id],
            mg_sum_squaredscores[milestone_group_id],
        )

    session.commit()
    logger.info("  - done")
    return f"Statistics re-calculated using {len(milestone_answer_sessions)} answer sessions in {time.monotonic() - start_time:.1f}s."


def save_milestone_statistics(
    session: SessionDep, milestone_id: int, counts: np.ndarray
) -> None:
    """
    Construct a MilestoneAgeScoreCollection of MilestoneAgeScores for a milestone using the supplied statistics.

    Parameters
    ----------
    session: SessionDep
        the database session
    milestone_id : int
        id of the milestone to calculate the statistics for
    counts: np.ndarray
        the counts of each answer per age in months, where the index corresponds to the age in months, then the answer
    """
    collection = session.get(MilestoneAgeScoreCollection, milestone_id)
    if collection is None:
        collection = MilestoneAgeScoreCollection(
            milestone_id=milestone_id,
            expected_age=0,
            relevant_age_min=0,
            relevant_age_max=0,
        )
        session.add(collection)

    collection.expected_age = get_expected_age_from_scores(counts)
    collection.relevant_age_min, collection.relevant_age_max = get_relevant_age_min_max(
        collection.expected_age, counts
    )

    # ensure that we have a MilestoneAgeScore for this milestone for each child age up to the maximum child age
    if (
        session.get(
            MilestoneAgeScore,
            ({"milestone_id": milestone_id, "age": app_settings.MAX_CHILD_AGE_MONTHS}),
        )
        is None
    ):
        for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
            score = session.get(
                MilestoneAgeScore, ({"milestone_id": milestone_id, "age": age})
            )
            if score is None:
                score = MilestoneAgeScore(
                    age=age,
                    milestone_id=milestone_id,
                    c0=0,
                    c1=0,
                    c2=0,
                    c3=0,
                )
                session.add(score)
    # do a bulk update of the MilestoneAgeScores for this milestone
    session.execute(
        update(MilestoneAgeScore),
        [
            {
                "age": age,
                "milestone_id": milestone_id,
                "c0": int(counts[age][0]),
                "c1": int(counts[age][1]),
                "c2": int(counts[age][2]),
                "c3": int(counts[age][3]),
            }
            for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1)
        ],
    )


def save_milestone_group_statistics(
    session: SessionDep,
    milestone_group_id: int,
    count: np.ndarray,
    sum_scores: np.ndarray,
    sum_squaredscores: np.ndarray,
) -> None:
    """
    Construct a MilestoneGroupAgeScoreCollection of MilestoneGroupAgeScores for a milestone using the supplied statistics.

    Parameters
    ----------
    session: SessionDep
        the database session
    milestone_group_id : int
        id of the milestone group to calculate the statistics for
    count: np.ndarray
        the count of answers per age in months, where the index corresponds to the age in months
    sum_scores: np.ndarray
        the sum of scores per age in months, where the index corresponds to the age in months
    sum_squaredscores: np.ndarray
        the sum of scores squared per age in months, where the index corresponds to the age in months
    """

    collection = session.get(MilestoneGroupAgeScoreCollection, milestone_group_id)

    if collection is None:
        collection = MilestoneGroupAgeScoreCollection(
            milestone_group_id=milestone_group_id
        )
        session.add(collection)

    # ensure that we have a MilestoneGroupAgeScore for this milestone for each child age up to the maximum child age
    if (
        session.get(
            MilestoneGroupAgeScore,
            (
                {
                    "milestone_group_id": milestone_group_id,
                    "age": app_settings.MAX_CHILD_AGE_MONTHS,
                }
            ),
        )
        is None
    ):
        for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
            score = session.get(
                MilestoneGroupAgeScore,
                ({"milestone_group_id": milestone_group_id, "age": age}),
            )
            if score is None:
                score = MilestoneGroupAgeScore(
                    age=age,
                    milestone_group_id=milestone_group_id,
                    count=0,
                    sum_score=0.0,
                    sum_squaredscore=0.0,
                )
                session.add(score)

    # do a bulk update of the MilestoneGroupAgeScores for this milestone group
    session.execute(
        update(MilestoneGroupAgeScore),
        [
            {
                "age": age,
                "milestone_group_id": milestone_group_id,
                "count": int(count[age]),
                "sum_score": sum_scores[age],
                "sum_squaredscore": sum_squaredscores[age],
            }
            for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1)
        ],
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
    milestone_answers: pd.DataFrame,
    user_answers: pd.DataFrame,
    child_answers: pd.DataFrame,
    child_ages: dict[int, int],
) -> pd.DataFrame:
    datatable: list[dict[str, str | int | float]] = []
    for milestone_answer_session in milestone_answer_sessions:
        child_age = child_ages.get(milestone_answer_session.id)  # type: ignore
        if child_age is not None:
            row = {
                "child_age": child_age,
                "answer_session_id": milestone_answer_session.id,
                "user_id": milestone_answer_session.user_id,
                "child_id": milestone_answer_session.child_id,
            }
            datatable.append(row)  # type: ignore
    df = pd.DataFrame(datatable)
    if "answer_session_id" in df.columns:
        df.set_index("answer_session_id", inplace=True)
    df = df.merge(milestone_answers, how="left", left_index=True, right_index=True)
    if "user_id" in df.columns:
        df = df.merge(user_answers, how="left", left_on="user_id", right_index=True)
        df.drop(columns=["user_id"], inplace=True)
    if "child_id" in df.columns:
        df = df.merge(child_answers, how="left", left_on="child_id", right_index=True)
        df.drop(columns=["child_id"], inplace=True)
    return df


def get_milestone_answers(session: SessionDep) -> pd.DataFrame:
    milestone_ids = session.exec(select(Milestone.id).order_by(col(Milestone.id))).all()
    milestone_answers: dict[int, dict[str, int]] = defaultdict(dict)
    for answer in session.exec(select(MilestoneAnswer)).all():
        milestone_answers[answer.answer_session_id][  # type: ignore
            f"milestone_id_{answer.milestone_id}"
        ] = answer.answer
    df = pd.DataFrame.from_dict(
        milestone_answers,
        orient="index",
        columns=[f"milestone_id_{milestone_id}" for milestone_id in milestone_ids],
    )
    return df


def get_answers(
    session: SessionDep,
    answer_type_name: str,
) -> pd.DataFrame:
    if answer_type_name == "user":
        question_type = UserQuestion
        answer_type = UserAnswer
    elif answer_type_name == "child":
        question_type = ChildQuestion  # type: ignore
        answer_type = ChildAnswer  # type: ignore
    else:
        raise ValueError(
            f"Invalid answer_type_name '{answer_type_name}': must be 'user' or 'child'"
        )
    question_additional_options = {
        q.id: q.additional_option
        for q in session.exec(
            select(question_type).order_by(col(question_type.id))
        ).all()
    }
    answers: dict[int, dict[str, str | int | float]] = defaultdict(dict)
    for answer in session.exec(select(answer_type)).all():
        answer_value = answer.answer
        # if the selected answer is the additional option, use the additional answer instead
        if (
            answer_value == question_additional_options.get(answer.question_id)
            and answer.additional_answer
        ):
            answer_value = answer.additional_answer
        answers[getattr(answer, f"{answer_type_name}_id")][
            f"{answer_type_name}_question_{answer.question_id}"
        ] = answer_value
    df = pd.DataFrame.from_dict(
        answers,
        orient="index",
        columns=[
            f"{answer_type_name}_question_{question_id}"
            for question_id in question_additional_options
        ],
    )
    return df


async def extract_research_data(
    session: SessionDep,
    user_session: UserAsyncSessionDep,
    research_group_id: int | None = None,
) -> pd.DataFrame:
    logger.info("Extracting research data...")
    test_user_ids_to_exclude = await get_test_account_user_ids(user_session)
    logger.info(
        f"  - collected {len(test_user_ids_to_exclude)} test user ids to exclude"
    )
    answer_session_filter = (
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.completed))
        .where(col(MilestoneAnswerSession.user_id).not_in(test_user_ids_to_exclude))
    )
    if research_group_id is not None:
        user_ids = await get_user_ids(user_session, research_group_id)
        answer_session_filter = answer_session_filter.where(
            col(MilestoneAnswerSession.user_id).in_(user_ids)
        )
    milestone_answer_sessions = session.exec(answer_session_filter).all()
    logger.info(
        f"  - collected {len(milestone_answer_sessions)} milestone answer sessions"
    )
    milestone_answers = get_milestone_answers(session)
    logger.info(f"  - collected {len(milestone_answers)} milestone answers")
    child_ages = get_answer_session_child_ages_in_months(
        session, milestone_answer_sessions
    )
    logger.info(f"  - collected {len(child_ages)} child ages")
    user_answers = get_answers(session, "user")
    logger.info(f"  - collected {len(user_answers)} user answers")
    child_answers = get_answers(session, "child")
    logger.info(f"  - collected {len(child_answers)} child answers")
    datatable = make_datatable(
        milestone_answer_sessions,
        milestone_answers,
        user_answers,
        child_answers,
        child_ages,
    )
    logger.info("...done")
    return datatable
