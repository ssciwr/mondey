from __future__ import annotations

import datetime
from collections import defaultdict
from collections.abc import Sequence

import numpy as np
import pandas as pd
from sqlmodel import col
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
from mondey_backend.routers.utils import get_expected_age_delta
from mondey_backend.routers.utils import get_expected_age_from_scores
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
        score = session.exec(
            select(MilestoneAgeScore)
            .where(col(MilestoneAgeScore.age) == child_age)
            .where(col(MilestoneAgeScore.milestone_id) == milestone_id)
        ).one_or_none()
        if score is None:
            logger.warning(
                f"    - no statistics available for milestone {milestone_id} - skipping"
            )
            continue
        analysis.answers.append(
            MilestoneAnswerAnalysis(
                milestone_id=milestone_id,
                answer=answer.answer,
                avg_answer=score.avg_score,
                stddev_answer=score.stddev_score,
            )
        )
        diff += np.power(score.avg_score - answer.answer, 2)
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
    for milestone_answer_session in session.exec(
        select(MilestoneAnswerSession).where(col(MilestoneAnswerSession.completed))
    ).all():
        for answer in milestone_answer_session.answers.values():
            if answer.answer < 0:
                logger.warning(
                    f"Answer session {milestone_answer_session.id} was marked completed but has missing answers, marking as incomplete"
                )
                milestone_answer_session.completed = False
                session.add(milestone_answer_session)
                break
        session.commit()


def flag_suspicious_answer_sessions(
    session: SessionDep,
    test_account_user_ids_to_exclude: list[int],
    threshold: float = 1.0,
):
    """
    Flag any new answer sessions with rms difference to average answers for that age greater than `threshold` as suspicious.
    Only updates sessions that haven't been manually tagged by an admin.
    """
    milestone_answer_sessions = session.exec(
        select(MilestoneAnswerSession)
        .where(col(MilestoneAnswerSession.completed))
        .where(
            col(MilestoneAnswerSession.suspicious_state)
            == SuspiciousState.not_suspicious
            # only consider these to mark as suspicious
            # i.e. ignore any admin set ones at this point.
        )
        .where(
            col(MilestoneAnswerSession.user_id).not_in(test_account_user_ids_to_exclude)
        )
        .where(~col(MilestoneAnswerSession.included_in_statistics))
    ).all()
    logger.debug(
        f"  - found {len(milestone_answer_sessions)} answer sessions to check for suspiciousness"
    )
    for milestone_answer_session in milestone_answer_sessions:
        try:
            analysis = analyse_answer_session(session, milestone_answer_session)
            if analysis.rms > threshold:
                logger.debug(
                    f"Marking answer session {milestone_answer_session.id} with rms difference {analysis.rms} as suspicious"
                )
                milestone_answer_session.suspicious_state = SuspiciousState.suspicious
                session.add(milestone_answer_session)
        except AttributeError as e:
            logger.exception(e)
    session.commit()


def create_age_score_collections_if_missing(session: SessionDep) -> None:
    for milestone_id in session.exec(select(Milestone.id)).all():
        if session.get(MilestoneAgeScoreCollection, milestone_id) is None:
            collection = MilestoneAgeScoreCollection(
                milestone_id=milestone_id, expected_age=12, expected_age_delta=6
            )
            session.add(collection)
            for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
                score = MilestoneAgeScore(
                    age=age,
                    milestone_id=milestone_id,
                    n0=0,
                    n1=0,
                    n2=0,
                    n3=0,
                    avg_score=0.0,
                    stddev_score=0.0,
                )
                session.add(score)
    for milestone_group_id in session.exec(select(MilestoneGroup.id)).all():
        if session.get(MilestoneGroupAgeScoreCollection, milestone_group_id) is None:
            collection = MilestoneGroupAgeScoreCollection(
                milestone_group_id=milestone_group_id,
                expected_age=12,
                expected_age_delta=6,
            )
            session.add(collection)
            for age in range(0, app_settings.MAX_CHILD_AGE_MONTHS + 1):
                score = MilestoneGroupAgeScore(
                    age=age,
                    milestone_group_id=milestone_group_id,
                    n0=0,
                    n1=0,
                    n2=0,
                    n3=0,
                    avg_score=0.0,
                    stddev_score=0.0,
                )
                session.add(score)
    session.commit()


def update_score(score: MilestoneAgeScore | MilestoneGroupAgeScore, answer: int):
    if answer == 0:
        score.n0 += 1
    elif answer == 1:
        score.n1 += 1
    elif answer == 2:
        score.n2 += 1
    elif answer == 3:
        score.n3 += 1


def update_age_score_collection_avg_std_dev(
    score_collection: MilestoneAgeScoreCollection | MilestoneGroupAgeScoreCollection,
):
    """
    Update the average and standard deviation of each score in the given score collection from the counts of each answer.

    $N = n_0+n_1+n_2+n_3$
    $\langle X \rangle = (n_1 + 2n_2 + 3n_3)/N$
    $\langle X^2 \rangle = (n_1 + 4 n_2 + 9n_3)/N$
    $\sigma^2 = \langle X^2 \rangle - \langle X \rangle^2$
    """
    minimum_number_of_samples = 2
    for score in score_collection.scores:
        count = score.n0 + score.n1 + score.n2 + score.n3
        if count == 0:
            score.avg_score = 0.0
            score.stddev_score = 0.0
        else:
            score.avg_score = (score.n1 + 2 * score.n2 + 3 * score.n3) / count
            if count < minimum_number_of_samples:
                score.stddev_score = -1.0
            else:
                score.stddev_score = np.sqrt(
                    (score.n1 + 4 * score.n2 + 9 * score.n3) / count
                    - np.pow(score.avg_score, 2)
                )


def update_age_score_collections_avg_std_dev(session: SessionDep):
    for score_collection in session.exec(select(MilestoneAgeScoreCollection)).all():
        update_age_score_collection_avg_std_dev(score_collection)
    for group_score_collection in session.exec(
        select(MilestoneGroupAgeScoreCollection)
    ).all():
        update_age_score_collection_avg_std_dev(group_score_collection)


async def async_update_stats(
    session: SessionDep,
    user_session: UserAsyncSessionDep,
    incremental_update: bool = True,
):
    """Update the recorded statistics of the milestonegroups and milestones.
    It only uses completed milestoneanswersesssions, excluding those from test users or those that are marked as suspicious.
    Args:
        session (SessionDep): database session
        user_session (UserAsyncSessionDep): user session
        incremental_update (bool, optional): If True (default) only update stats with new data, otherwise recalculate all statistics.

    Returns:
        str: Message string indicating successful statistics update
    """
    logger.debug(
        f"Starting {'incremental' if incremental_update else 'full'} statistics update"
    )

    flag_incomplete_answer_sessions(session)

    # We gather these first then exclude later so that we don't do a FK join on the user_id<->email for stale+filtering
    test_account_user_ids_to_exclude = await get_test_account_user_ids(user_session)

    flag_suspicious_answer_sessions(session, test_account_user_ids_to_exclude)

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

    if incremental_update:
        answer_session_filter = answer_session_filter.where(
            ~col(MilestoneAnswerSession.included_in_statistics)
        )
    milestone_answer_sessions = session.exec(answer_session_filter).all()

    child_ages = get_answer_session_child_ages_in_months(
        session, milestone_answer_sessions
    )
    logger.debug(f"  - found {len(milestone_answer_sessions)} answer sessions")
    logger.debug(f"    {[m.id for m in milestone_answer_sessions]}")

    create_age_score_collections_if_missing(session)

    # update answer counts for each Milestone and MilestoneGroup
    logger.debug("  - updating answer counts...")
    milestones = session.exec(select(Milestone)).all()
    for milestone_answer_session in milestone_answer_sessions:
        for milestone in milestones:
            age = child_ages[milestone_answer_session.id]  # type: ignore
            answer = milestone_answer_session.answers.get(milestone.id)  # type: ignore
            if answer is not None:
                # if there is an answer for this milestone, update the count for the milestone age score
                milestone_score = session.get(
                    MilestoneAgeScore, {"milestone_id": milestone.id, "age": age}
                )
                update_score(milestone_score, answer.answer)
            # even if a milestone is not included in the answer session, we still need a value when calculating
            # the average and std dev of answers for the milestone group.
            # We assume a full score if the child is older than the expected age for the milestone,
            # and a zero score if child is younger.
            answer_value = (
                answer.answer
                if answer is not None
                else (3 if milestone.expected_age_months < age else 0)
            )  # type: ignore
            milestone_group_score = session.get(
                MilestoneGroupAgeScore, {"milestone_group_id": milestone.id, "age": age}
            )
            update_score(milestone_group_score, answer_value)
        milestone_answer_session.included_in_statistics = True

    logger.debug("  - recalculating avg/std_dev values...")
    update_age_score_collections_avg_std_dev(session)

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
    session: SessionDep,
    milestone_id: int,
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    incremental_update: bool,
) -> None:
    """
    Calculate the mean, variance of a milestone per age in months,
    and update or create a MilestoneAgeScoreCollection of MilestoneAgeScores for this milestone.
    If incremental_update is True then the supplied answers are added to the existing statistics,
    otherwise the statistics are recalculated from scratch.

    Parameters
    ----------
    session: SessionDep
        the database session
    milestone_id : int
        id of the milestone to calculate the statistics for
    answers: Sequence[MilestoneAnswer]
        the new answers to include in the statistics.
    child_ages : dict[int, int]
        dict of answer_session_id -> child age in months
    incremental_update: bool
        if True, add the new answers to the existing statistics, otherwise recalculate the statistics from scratch
    """
    if len(answers) == 0:
        return

    collection = session.get(MilestoneAgeScoreCollection, milestone_id)

    expected_age = get_expected_age_from_scores(avg_scores, count)

    expected_age_delta = get_expected_age_delta(expected_age, avg_scores, count)

    if collection is None:
        collection = MilestoneAgeScoreCollection(
            milestone_id=milestone_id,
            expected_age=expected_age,
            expected_age_delta=expected_age_delta,
            created_at=datetime.datetime.now(),
        )
        session.add(collection)
    else:
        collection.expected_age = expected_age
        collection.expected_age_delta = expected_age_delta

    for age in range(0, len(avg_scores)):
        score = session.get(
            MilestoneAgeScore, ({"milestone_id": milestone_id, "age": age})
        )
        if score is None:
            score = MilestoneAgeScore(
                age=age,
                milestone_id=milestone_id,
                count=0,
                avg_score=0.0,
                stddev_score=0.0,
            )
        score.count = int(
            count[age]
        )  # need a conversion to avoid numpy.int32 being stored as byte object
        score.avg_score = avg_scores[age]
        score.stddev_score = stddev_scores[age]
        session.add(score)
    session.commit()


def calculate_milestonegroup_statistics_by_age(
    session: SessionDep,
    milestone_group_id: int,
    answers: Sequence[MilestoneAnswer],
    child_ages: dict[int, int],
    incremental_update: bool,
) -> None:
    """
    Calculate the mean, variance of a milestone group per age in months.
    and update or create a MilestoneGroupAgeScoreCollection of MilestoneGroupAgeScores for this milestone.
    If incremental_update is True then the supplied answers are added to the existing statistics,
    otherwise the statistics are recalculated from scratch.

    Parameters
    ----------
    session: SessionDep
        the database session
    milestone_group_id : int
        id of the milestone group to calculate the statistics for
    answers: Sequence[MilestoneAnswer]
        the new answers to include in the statistics.
    child_ages : dict[int, int]
        dict of answer_session_id -> child age in months
    incremental_update: bool
        if True, add the new answers to the existing statistics, otherwise recalculate the statistics from scratch
    Returns
    -------
    None
    """
    if len(answers) == 0:
        return

    collection = session.get(MilestoneGroupAgeScoreCollection, milestone_group_id)

    # initialize avg and stddev scores with any existing statistics if doing an incremental update
    count, avg_scores, stddev_scores = _extract_stats(
        collection if incremental_update else None
    )

    count, avg_scores, stddev_scores = _get_statistics_by_age(
        answers, child_ages, count=count, avg=avg_scores, stddev=stddev_scores
    )

    if collection is None:
        collection = MilestoneGroupAgeScoreCollection(
            milestone_group_id=milestone_group_id
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)

    for age in range(0, len(avg_scores)):
        score = session.get(
            MilestoneGroupAgeScore,
            ({"milestone_group_id": milestone_group_id, "age": age}),
        )
        if score is None:
            score = MilestoneGroupAgeScore(
                age=age,
                milestone_group_id=milestone_group_id,
                count=0,
                avg_score=0.0,
                stddev_score=0.0,
            )
        score.count = int(
            count[age]
        )  # need a conversion to avoid numpy.int32 being stored as byte object
        score.avg_score = avg_scores[age]
        score.stddev_score = stddev_scores[age]
        session.add(score)
    session.commit()


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
