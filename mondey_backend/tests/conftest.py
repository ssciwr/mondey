from __future__ import annotations

import datetime
import pathlib

import numpy as np
import pytest
import pytest_asyncio
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool

from mondey_backend import settings
from mondey_backend.databases.users import get_async_session
from mondey_backend.dependencies import current_active_researcher
from mondey_backend.dependencies import current_active_superuser
from mondey_backend.dependencies import current_active_user
from mondey_backend.dependencies import get_session
from mondey_backend.main import create_app
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.models.milestones import MilestoneGroupText
from mondey_backend.models.milestones import MilestoneImage
from mondey_backend.models.milestones import MilestoneText
from mondey_backend.models.milestones import SubmittedMilestoneImage
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText
from mondey_backend.models.research import ResearchGroup
from mondey_backend.models.users import Base
from mondey_backend.models.users import User
from mondey_backend.models.users import UserRead


@pytest.fixture()
def static_dir(tmp_path_factory: pytest.TempPathFactory):
    static_dir = tmp_path_factory.mktemp("static")
    # add some milestone image files
    milestone_images_dir = static_dir / "m"
    milestone_images_dir.mkdir()
    for milestone_image_id in [1, 2, 3]:
        img = Image.new("RGB", (201, 414))
        img.save(milestone_images_dir / f"{milestone_image_id}.webp")
    # add user submitted milestone image files
    submitted_milestone_images_dir = static_dir / "ms"
    submitted_milestone_images_dir.mkdir()
    for submitted_milestone_image_id in [1, 2]:
        img = Image.new("RGB", (281, 311))
        img.save(
            submitted_milestone_images_dir / f"{submitted_milestone_image_id}.webp"
        )
    # add some i18n json files
    i18n_dir = static_dir / "i18n"
    i18n_dir.mkdir()
    for lang in ["de", "en", "fr"]:
        (i18n_dir / f"{lang}.json").write_text("{}")
    return static_dir


@pytest.fixture()
def private_dir(tmp_path_factory: pytest.TempPathFactory):
    private_dir = tmp_path_factory.mktemp("private")
    children_dir = private_dir / "children"
    children_dir.mkdir()
    # add some child image files
    for child_id in [2, 3]:
        img = Image.new("RGBA", (67, 38))
        img.save(children_dir / f"{child_id}.webp")
    return private_dir


@pytest.fixture
def children():
    today = datetime.datetime.today()

    nine_months_ago = today - relativedelta(months=9)
    twenty_months_ago = today - relativedelta(months=20)
    fiftyfive_months_ago = today - relativedelta(months=55)
    return [
        # ~9month old child for user (id 3)
        {
            "id": 1,
            "name": "child1",
            "birth_year": nine_months_ago.year,
            "birth_month": nine_months_ago.month,
            "has_image": False,
            "color": "#f0f0ff",
        },
        # ~20month old child for user (id 3)
        {
            "id": 2,
            "name": "child2",
            "birth_year": twenty_months_ago.year,
            "birth_month": twenty_months_ago.month,
            "has_image": True,
            "color": "#ffffff",
        },
        # ~55month old child for admin user (id 1)
        {
            "birth_month": fiftyfive_months_ago.month,
            "birth_year": fiftyfive_months_ago.year,
            "id": 3,
            "name": "child3",
            "has_image": True,
            "color": "#ffffff",
        },
        # ~9month old child for test account user (id 5)
        {
            "id": 4,
            "name": "child4 (test account user)",
            "birth_year": nine_months_ago.year,
            "birth_month": nine_months_ago.month,
            "has_image": False,
            "color": "#c0c0c0",
        },
    ]


@pytest_asyncio.fixture(loop_scope="function")
async def user_session(
    active_admin_user: UserRead,
    active_research_user: UserRead,
    active_user: UserRead,
    active_user2: UserRead,
    active_test_account_user: UserRead,
    monkeypatch: pytest.MonkeyPatch,
):
    # use a new in-memory SQLite user database for each test
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    # we also need to monkey patch the async_session_maker which is directly used in the users module
    monkeypatch.setattr("mondey_backend.users.async_session_maker", async_session_maker)
    async with async_session_maker() as session:
        for user_read in [
            active_admin_user,
            active_research_user,
            active_user,
            active_user2,
            active_test_account_user,
        ]:
            user = User(hashed_password="abc")
            for k, v in user_read.model_dump().items():
                setattr(user, k, v)
            session.add(user)
        await session.commit()
        yield session


@pytest.fixture
def session(children: list[dict], monkeypatch: pytest.MonkeyPatch):
    # use a new in-memory SQLite database for each test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    # we also need to monkey patch the mondey_engine which is directly used in the users module
    monkeypatch.setattr("mondey_backend.users.mondey_engine", engine)
    # add some test data
    with Session(engine) as session:
        # add 3 languages
        lang_ids = ["de", "en", "fr"]
        for lang_id in lang_ids:
            session.add(Language(id=lang_id))
        # add a milestone group with 3 milestones
        session.add(MilestoneGroup(order=2))
        for lang_id in lang_ids:
            lbl = f"g1_{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=1, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )
        for milestone_id in [1, 2, 3]:
            # milestones have expected ages 6*id +/- 2*(id+1), so 6 +/- 4, 12 +/- 6, ...
            session.add(
                Milestone(
                    name=f"m{milestone_id}",
                    order=14 - milestone_id,
                    group_id=1,
                    expected_age_months=milestone_id * 6,
                    expected_age_delta=(milestone_id + 1) * 2,
                )
            )
            for lang_id in lang_ids:
                lbl = f"m{milestone_id}_{lang_id}"
                session.add(
                    MilestoneText(
                        milestone_id=milestone_id,
                        lang_id=lang_id,
                        title=f"{lbl}_t",
                        desc=f"{lbl}_d",
                        obs=f"{lbl}_o",
                        help=f"{lbl}_h",
                        importanceOfMilestone="",
                    )
                )

        # add a second milestone group with 2 milestones
        session.add(MilestoneGroup(order=1))
        for lang_id in lang_ids:
            lbl = f"g1_{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=2, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )

        for milestone_id in [4, 5]:
            session.add(
                Milestone(
                    name=f"m{milestone_id}",
                    order=milestone_id,
                    group_id=2,
                    expected_age_months=milestone_id * 6,
                    expected_age_delta=(milestone_id + 1) * 2,
                )
            )
            for lang_id in lang_ids:
                lbl = f"m{milestone_id}_{lang_id}"
                session.add(
                    MilestoneText(
                        milestone_id=milestone_id,
                        lang_id=lang_id,
                        title=f"{lbl}_t",
                        desc=f"{lbl}_d",
                        obs=f"{lbl}_o",
                        help=f"{lbl}_h",
                        importanceOfMilestone="",
                    )
                )
        # add the milestone images and submitted milestone images that were created in the static directory
        session.add(MilestoneImage(milestone_id=1, filename="m1.jpg", approved=True))
        session.add(MilestoneImage(milestone_id=1, filename="m2.jpg", approved=True))
        session.add(MilestoneImage(milestone_id=2, filename="m3.jpg", approved=True))
        session.add(SubmittedMilestoneImage(milestone_id=1, user_id=1))
        session.add(SubmittedMilestoneImage(milestone_id=2, user_id=2))
        session.commit()
        for child, user_id in zip(children, [3, 3, 1, 5], strict=False):
            session.add(Child.model_validate(child, update={"user_id": user_id}))
        today = datetime.datetime.today()
        last_month = today - relativedelta(months=1)
        # expired, completed, included in stats milestone answer session for child 1 / user (id 3) with 2 answers
        session.add(
            MilestoneAnswerSession(
                id=1,
                child_id=1,
                user_id=3,
                created_at=datetime.datetime(last_month.year, last_month.month, 15),
                expired=True,
                completed=True,
                included_in_statistics=True,
                suspicious_state=SuspiciousState.not_suspicious,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=1,
                milestone_id=1,
                milestone_group_id=1,
                answer=1,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=1,
                milestone_id=2,
                milestone_group_id=1,
                answer=0,
            )
        )
        # expired, completed, not yet included in stats milestone answer session for child 1 / user (id 3) with 2 answers to the same questions
        session.add(
            MilestoneAnswerSession(
                id=2,
                child_id=1,
                user_id=3,
                created_at=datetime.datetime(last_month.year, last_month.month, 20),
                completed=True,
                expired=True,
                included_in_statistics=False,
                suspicious_state=SuspiciousState.unknown,
            )
        )
        # add two milestone answers
        session.add(
            MilestoneAnswer(
                answer_session_id=2, milestone_id=1, milestone_group_id=1, answer=1
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=2, milestone_id=2, milestone_group_id=1, answer=1
            )
        )
        # un-expired, completed milestone answer session for child 3 / admin user (id 1) with 1 answer
        session.add(
            MilestoneAnswerSession(
                id=3,
                child_id=3,
                user_id=1,
                created_at=datetime.datetime.today(),
                completed=True,
                expired=True,
                included_in_statistics=False,
                suspicious_state=SuspiciousState.unknown,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=3,
                milestone_id=5,
                milestone_group_id=2,
                answer=2,
            )
        )
        # un-expired, incompleted milestone answer session for child 3 / admin user (id 1) with 1 missing answer
        session.add(
            MilestoneAnswerSession(
                id=6,
                child_id=3,
                user_id=1,
                created_at=datetime.datetime.today(),
                completed=False,
                expired=False,
                included_in_statistics=False,
                suspicious_state=SuspiciousState.unknown,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=6,
                milestone_id=5,
                milestone_group_id=2,
                answer=-1,
            )
        )
        # expired, completed, not included in stats milestoneanswersession for milestones 1, 2 for child 1
        session.add(
            MilestoneAnswerSession(
                id=4,
                child_id=1,
                user_id=3,
                created_at=datetime.datetime(last_month.year, last_month.month, 20),
                completed=True,
                expired=True,
                included_in_statistics=False,
                suspicious_state=SuspiciousState.unknown,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=4, milestone_id=1, milestone_group_id=1, answer=2
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=4, milestone_id=2, milestone_group_id=1, answer=0
            )
        )

        # expired, incomplete, not included in stats answersession for child 3 with answers for milestone 7 & 8, 1 year ago
        session.add(
            MilestoneAnswerSession(
                id=5,
                child_id=3,
                user_id=1,
                created_at=datetime.datetime(today.year - 1, today.month, 10),
                completed=False,
                expired=True,
                included_in_statistics=False,
                suspicious_state=SuspiciousState.unknown,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=5, milestone_id=5, milestone_group_id=2, answer=-1
            )
        )

        # expired, completed, included in stats milestone answer session for child 4 / test account user (id 5) with 2 answers
        session.add(
            MilestoneAnswerSession(
                id=99,
                child_id=4,
                user_id=5,
                created_at=datetime.datetime(last_month.year, last_month.month, 15),
                completed=True,
                expired=True,
                included_in_statistics=True,
                suspicious_state=SuspiciousState.not_suspicious,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=99,
                milestone_id=1,
                milestone_group_id=1,
                answer=1,
            )
        )
        session.add(
            MilestoneAnswer(
                answer_session_id=99,
                milestone_id=2,
                milestone_group_id=1,
                answer=0,
            )
        )

        # add MilestoneAgeScoreCollection for milestone 1
        session.add(
            MilestoneAgeScoreCollection(
                milestone_id=1,
                expected_age=8,
                expected_age_delta=4,
            )
        )
        for age in range(0, settings.app_settings.MAX_CHILD_AGE_MONTHS + 1):
            session.add(
                MilestoneAgeScore(
                    age=age,
                    milestone_id=1,
                    c0=0,
                    c1=1 if age == 8 else 0,
                    c2=0,
                    c3=0,
                )
            )

        # add MilestoneAgeScoreCollection for milestone 2
        session.add(
            MilestoneAgeScoreCollection(
                milestone_id=2,
                expected_age=8,
                expected_age_delta=4,
            )
        )
        for age in range(0, settings.app_settings.MAX_CHILD_AGE_MONTHS + 1):
            session.add(
                MilestoneAgeScore(
                    age=age,
                    milestone_id=2,
                    c0=1 if age == 8 else 0,
                    c1=0,
                    c2=0,
                    c3=0,
                )
            )

        # add MilestoneGroupAgeScoreCollection for milestone group 1
        session.add(
            MilestoneGroupAgeScoreCollection(
                milestone_group_id=1,
            )
        )
        age_8_milestone_group1_scores = (
            1,
            0,
            0,
        )  # answers for milestone 1,2,3 from answer session 1 (#3 is imputed)
        avg_score = np.mean(age_8_milestone_group1_scores)
        for age in range(0, settings.app_settings.MAX_CHILD_AGE_MONTHS + 1):
            session.add(
                MilestoneGroupAgeScore(
                    age=age,
                    milestone_group_id=1,
                    count=1 if age == 8 else 0,
                    sum_score=avg_score if age == 8 else 0.0,
                    sum_squaredscore=avg_score * avg_score if age == 8 else 0.0,
                )
            )

        # add a research group (that user with id 3 is part of, and researcher with id 2 has access to)
        session.add(ResearchGroup(id="123451"))
        # add user questions for admin
        user_questions = [
            UserQuestion(
                id=1,
                order=1,
                name="User Question 1",
                options="[a,b,c,other]",
                additional_option="other",
                component="select",
                text={
                    "de": UserQuestionText(
                        user_question_id=1,
                        lang_id="de",
                        options="[x,y,z]",
                        question="Wo sonst?",
                        options_json="",
                    ),
                    "en": UserQuestionText(
                        user_question_id=1,
                        lang_id="en",
                        options="[1,2,3]",
                        question="Where else?",
                        options_json="",
                    ),
                    "fr": UserQuestionText(
                        user_question_id=1,
                        lang_id="fr",
                        options="[1,2,3]",
                        question="french words",
                        options_json="",
                    ),
                },
                visibility=True,
            ),
            UserQuestion(
                id=2,
                order=2,
                name="User Question 2",
                component="textarea",
                options="[a2,b2,c2,other]",
                additional_option="other",
                text={
                    "de": UserQuestionText(
                        user_question_id=2,
                        lang_id="de",
                        options="[x2,y2,z2]",
                        question="Was noch?",
                        options_json="",
                    ),
                    "en": UserQuestionText(
                        user_question_id=2,
                        lang_id="en",
                        options="[12,22,32]",
                        question="What else?",
                        options_json="",
                    ),
                    "fr": UserQuestionText(
                        user_question_id=2,
                        lang_id="fr",
                        options="[12,22,32]",
                        question="french words",
                        options_json="",
                    ),
                },
                visibility=True,
            ),
            UserQuestion(
                id=3,
                order=3,
                name="User Question 3 - Should not be visible",
                options="[a,b,c,other]",
                additional_option="other",
                component="select",
                text={
                    "de": UserQuestionText(
                        user_question_id=3,
                        lang_id="de",
                        options="[x,y,z]",
                        question="Wo sonst 3?",
                        options_json="",
                    ),
                    "en": UserQuestionText(
                        user_question_id=3,
                        lang_id="en",
                        options="[1,2,3]",
                        question="Where else 3?",
                        options_json="",
                    ),
                    "fr": UserQuestionText(
                        user_question_id=3,
                        lang_id="fr",
                        options="[1,2,3]",
                        question="french words 3",
                        options_json="",
                    ),
                },
                visibility=False,
            ),
        ]
        for user_question in user_questions:
            session.add(user_question)
            for lang in user_question.text:
                session.add(user_question.text[lang])

        # add child questions
        child_questions = [
            ChildQuestion(
                id=1,
                order=0,
                name="Child Question 1",
                options="[a,b,c,other]",
                additional_option="other",
                text={
                    "de": ChildQuestionText(
                        child_question_id=1,
                        lang_id="de",
                        question="was?",
                        options="[x,y,z,andere]",
                    ),
                    "en": ChildQuestionText(
                        child_question_id=1,
                        lang_id="en",
                        question="what?",
                        options="[1,2,3,other]",
                    ),
                    "fr": ChildQuestionText(
                        child_question_id=1,
                        lang_id="fr",
                        question="french...",
                        options="[1,2,3,autre]",
                    ),
                },
                visibility=True,
            ),
            ChildQuestion(
                id=2,
                order=1,
                name="Child Question 2",
                options="[a2,b2,c2,other]",
                additional_option="other",
                text={
                    "de": ChildQuestionText(
                        child_question_id=2,
                        lang_id="de",
                        question="Wo?",
                        options="[x2,y2,z2,andere]",
                    ),
                    "en": ChildQuestionText(
                        child_question_id=2,
                        lang_id="en",
                        question="Where?",
                        options="[12,22,32,other]",
                    ),
                    "fr": ChildQuestionText(
                        child_question_id=2,
                        lang_id="fr",
                        question="french...",
                        options="[12,22,32,autre]",
                    ),
                },
                visibility=True,
            ),
            ChildQuestion(
                id=3,
                order=2,
                name="Child Question 3",
                options="[a,b,c,other]",
                additional_option="other",
                text={
                    "de": ChildQuestionText(
                        child_question_id=1,
                        lang_id="de",
                        question="was?",
                        options="[x,y,z,andere]",
                    ),
                    "en": ChildQuestionText(
                        child_question_id=1,
                        lang_id="en",
                        question="what?",
                        options="[1,2,3,other]",
                    ),
                    "fr": ChildQuestionText(
                        child_question_id=1,
                        lang_id="fr",
                        question="french...",
                        options="[1,2,3,autre]",
                    ),
                },
                visibility=False,
            ),
        ]

        for child_question in child_questions:
            session.add(child_question)
            for lang in child_question.text:
                session.add(child_question.text[lang])

        # add user answers for user (id 3)
        session.add(
            UserAnswer(
                id=1,
                question_id=1,
                user_id=3,
                answer="lorem ipsum",
                additional_answer=None,
            )
        )
        session.add(
            UserAnswer(
                id=2,
                question_id=2,
                user_id=3,
                answer="other",
                additional_answer="dolor sit",
            )
        )

        # add child answers for user (id 3)
        session.add(
            ChildAnswer(
                id=1,
                question_id=1,
                user_id=3,
                child_id=1,
                answer="a",
                additional_answer=None,
            )
        )
        session.add(
            ChildAnswer(
                id=2,
                question_id=2,
                user_id=3,
                child_id=1,
                answer="other",
                additional_answer="apple",
            )
        )
        session.commit()
        yield session


visible_user_questions = [
    {
        "id": 1,
        "name": "User Question 1",
        "order": 1,
        "component": "select",
        "options": "[a,b,c,other]",
        "additional_option": "other",
        "required": False,
        "visibility": True,
        "type": "text",
        "text": {
            "de": {
                "user_question_id": 1,
                "lang_id": "de",
                "options": "[x,y,z]",
                "options_json": "",
                "question": "Wo sonst?",
            },
            "en": {
                "user_question_id": 1,
                "lang_id": "en",
                "options": "[1,2,3]",
                "question": "Where else?",
                "options_json": "",
            },
            "fr": {
                "user_question_id": 1,
                "lang_id": "fr",
                "options": "[1,2,3]",
                "question": "french words",
                "options_json": "",
            },
        },
    },
    {
        "id": 2,
        "name": "User Question 2",
        "order": 2,
        "component": "textarea",
        "options": "[a2,b2,c2,other]",
        "additional_option": "other",
        "required": False,
        "visibility": True,
        "type": "text",
        "text": {
            "de": {
                "user_question_id": 2,
                "lang_id": "de",
                "options": "[x2,y2,z2]",
                "options_json": "",
                "question": "Was noch?",
            },
            "en": {
                "user_question_id": 2,
                "lang_id": "en",
                "options": "[12,22,32]",
                "question": "What else?",
                "options_json": "",
            },
            "fr": {
                "user_question_id": 2,
                "lang_id": "fr",
                "options": "[12,22,32]",
                "question": "french words",
                "options_json": "",
            },
        },
    },
]


@pytest.fixture
def user_questions():
    return visible_user_questions


@pytest.fixture
def user_questions_with_invisible_question():
    return [
        *visible_user_questions,
        {
            "id": 3,
            "name": "User Question 3 - Should not be visible",
            "order": 3,
            "component": "select",
            "options": "[a,b,c,other]",
            "additional_option": "other",
            "required": False,
            "visibility": False,
            "type": "text",
            "text": {
                "de": {
                    "user_question_id": 3,
                    "lang_id": "de",
                    "options": "[x,y,z]",
                    "options_json": "",
                    "question": "Wo sonst 3?",
                },
                "en": {
                    "user_question_id": 3,
                    "lang_id": "en",
                    "options": "[1,2,3]",
                    "question": "Where else 3?",
                    "options_json": "",
                },
                "fr": {
                    "user_question_id": 3,
                    "lang_id": "fr",
                    "options": "[1,2,3]",
                    "question": "french words 3",
                    "options_json": "",
                },
            },
        },
    ]


visible_child_questions = [
    {
        "id": 1,
        "name": "Child Question 1",
        "order": 0,
        "component": "select",
        "options": "[a,b,c,other]",
        "additional_option": "other",
        "required": False,
        "visibility": True,
        "type": "text",
        "text": {
            "de": {
                "child_question_id": 1,
                "lang_id": "de",
                "options": "[x,y,z,andere]",
                "options_json": "",
                "question": "was?",
            },
            "en": {
                "child_question_id": 1,
                "lang_id": "en",
                "options": "[1,2,3,other]",
                "question": "what?",
                "options_json": "",
            },
            "fr": {
                "child_question_id": 1,
                "lang_id": "fr",
                "question": "french...",
                "options": "[1,2,3,autre]",
                "options_json": "",
            },
        },
    },
    {
        "id": 2,
        "name": "Child Question 2",
        "order": 1,
        "component": "select",
        "options": "[a2,b2,c2,other]",
        "additional_option": "other",
        "required": False,
        "visibility": True,
        "type": "text",
        "text": {
            "de": {
                "child_question_id": 2,
                "lang_id": "de",
                "options": "[x2,y2,z2,andere]",
                "options_json": "",
                "question": "Wo?",
            },
            "en": {
                "child_question_id": 2,
                "lang_id": "en",
                "options": "[12,22,32,other]",
                "question": "Where?",
                "options_json": "",
            },
            "fr": {
                "child_question_id": 2,
                "lang_id": "fr",
                "question": "french...",
                "options": "[12,22,32,autre]",
                "options_json": "",
            },
        },
    },
]


@pytest.fixture
def child_questions():
    return visible_user_questions


@pytest.fixture
def child_questions_with_invisible_question():
    return [
        *visible_child_questions,
        {
            "id": 3,
            "name": "Child Question 3",
            "order": 2,
            "component": "select",
            "options": "[a,b,c,other]",
            "additional_option": "other",
            "required": False,
            "visibility": False,
            "type": "text",
            "text": {
                "de": {
                    "child_question_id": 3,
                    "lang_id": "de",
                    "options": "[x,y,z,andere]",
                    "options_json": "",
                    "question": "was?",
                },
                "en": {
                    "child_question_id": 3,
                    "lang_id": "en",
                    "options": "[1,2,3,other]",
                    "question": "what?",
                    "options_json": "",
                },
                "fr": {
                    "child_question_id": 3,
                    "lang_id": "fr",
                    "question": "french...",
                    "options": "[1,2,3,autre]",
                    "options_json": "",
                },
            },
        },
    ]


@pytest.fixture
def child_answers():
    return {
        # name
        "1": {
            "answer": "other",
            "question_id": 1,
            "additional_answer": "sit amet",
        },
        # date
        "2": {
            "answer": "2024-03-02",
            "question_id": 2,
            "additional_answer": None,
        },
        # remark
        "3": {"answer": "some remark", "question_id": 3, "additional_answer": None},
        # file upload
        "4": {"answer": "file.jpg", "question_id": 4, "additional_answer": None},
    }


@pytest.fixture
def default_user_question_admin():
    return {
        "id": 1,
        "name": "User Question 1",
        "component": "textarea",
        "type": "other_thing",
        "order": 0,
        "options": "some_options",
        "text": {
            "de": {
                "options_json": "",
                "user_question_id": 1,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "user_question_id": 1,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "user_question_id": 1,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "nothing",
        "required": False,
        "visibility": False,
    }


@pytest.fixture
def active_admin_user():
    return UserRead(
        id=1,
        email="admin@mondey.de",
        is_active=True,
        is_superuser=True,
        is_researcher=True,
        full_data_access=True,
        research_group_id=0,
        is_verified=True,
    )


@pytest.fixture
def active_research_user():
    return UserRead(
        id=2,
        email="research@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=True,
        full_data_access=False,
        research_group_id=123451,
        is_verified=True,
    )


@pytest.fixture
def active_user():
    return UserRead(
        id=3,
        email="user@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        full_data_access=False,
        research_group_id=123451,
        is_verified=True,
    )


@pytest.fixture
def active_user2():
    return UserRead(
        id=4,
        email="user2@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        full_data_access=False,
        research_group_id=0,
        is_verified=True,
    )


@pytest.fixture
def active_test_account_user():
    return UserRead(
        id=5,
        email="abc123tester@testaccount.com",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        full_data_access=False,
        research_group_id=0,
        is_verified=True,
    )


@pytest.fixture
def active_research_user_full_data_access():
    return UserRead(
        id=6,
        email="research@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=True,
        full_data_access=True,
        research_group_id=485699,
        is_verified=True,
    )


@pytest.fixture(scope="function")
def app(
    static_dir: pathlib.Path,
    private_dir: pathlib.Path,
    session: Session,
    user_session: AsyncSession,
):
    settings.app_settings.STATIC_FILES_PATH = str(static_dir)
    settings.app_settings.PRIVATE_FILES_PATH = str(private_dir)
    settings.app_settings.SMTP_HOST = "smtp-host"
    settings.app_settings.SMTP_USERNAME = "test-smtp-username"
    settings.app_settings.SMTP_PASSWORD = "test-smtp-password"
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_async_session] = lambda: user_session
    yield app


@pytest.fixture
def public_client(app: FastAPI):
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_client(app: FastAPI, active_user: UserRead):
    app.dependency_overrides[current_active_user] = lambda: active_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_client2(
    app: FastAPI,
    active_user2: UserRead,
):
    app.dependency_overrides[current_active_user] = lambda: active_user2
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def research_client(
    app: FastAPI,
    active_research_user: UserRead,
):
    app.dependency_overrides[current_active_user] = lambda: active_research_user
    app.dependency_overrides[current_active_researcher] = lambda: active_research_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def research_client_full_data_access(
    app: FastAPI,
    active_research_user_full_data_access: UserRead,
):
    app.dependency_overrides[current_active_user] = (
        lambda: active_research_user_full_data_access
    )
    app.dependency_overrides[current_active_researcher] = (
        lambda: active_research_user_full_data_access
    )
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(
    app: FastAPI,
    session: Session,
    user_session: AsyncSession,
    active_admin_user: UserRead,
):
    app.dependency_overrides[current_active_user] = lambda: active_admin_user
    app.dependency_overrides[current_active_superuser] = lambda: active_admin_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def image_file_jpg_1600_1200(tmp_path: pathlib.Path):
    jpg_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (1600, 1200))
    img.save(jpg_path)
    return jpg_path


@pytest.fixture
def image_file_jpg_64_64(tmp_path: pathlib.Path):
    jpg_path = tmp_path / "test.jpg"
    img = Image.new("RGB", (64, 64))
    img.save(jpg_path)
    return jpg_path


@pytest.fixture
def image_file_png_1100_1100(tmp_path: pathlib.Path):
    png_path = tmp_path / "test.png"
    img = Image.new("RGBA", (1100, 1100))
    img.save(png_path)
    return png_path


@pytest.fixture
def milestone_group1():
    return {
        "id": 1,
        "text": {
            "de": {"title": "g1_de_t", "desc": "g1_de_d"},
            "en": {"title": "g1_en_t", "desc": "g1_en_d"},
            "fr": {"title": "g1_fr_t", "desc": "g1_fr_d"},
        },
        "milestones": [
            {
                "id": 3,
                "name": "m3",
                "text": {
                    "de": {
                        "title": "m3_de_t",
                        "desc": "m3_de_d",
                        "obs": "m3_de_o",
                        "help": "m3_de_h",
                        "importanceOfMilestone": "",
                    },
                    "en": {
                        "title": "m3_en_t",
                        "desc": "m3_en_d",
                        "obs": "m3_en_o",
                        "help": "m3_en_h",
                        "importanceOfMilestone": "",
                    },
                    "fr": {
                        "title": "m3_fr_t",
                        "desc": "m3_fr_d",
                        "obs": "m3_fr_o",
                        "help": "m3_fr_h",
                        "importanceOfMilestone": "",
                    },
                },
                "images": [],
            },
            {
                "id": 2,
                "name": "m2",
                "text": {
                    "de": {
                        "title": "m2_de_t",
                        "desc": "m2_de_d",
                        "obs": "m2_de_o",
                        "help": "m2_de_h",
                        "importanceOfMilestone": "",
                    },
                    "en": {
                        "title": "m2_en_t",
                        "desc": "m2_en_d",
                        "obs": "m2_en_o",
                        "help": "m2_en_h",
                        "importanceOfMilestone": "",
                    },
                    "fr": {
                        "title": "m2_fr_t",
                        "desc": "m2_fr_d",
                        "obs": "m2_fr_o",
                        "help": "m2_fr_h",
                        "importanceOfMilestone": "",
                    },
                },
                "images": [{"id": 3}],
            },
            {
                "id": 1,
                "name": "m1",
                "text": {
                    "de": {
                        "title": "m1_de_t",
                        "desc": "m1_de_d",
                        "obs": "m1_de_o",
                        "help": "m1_de_h",
                        "importanceOfMilestone": "",
                    },
                    "en": {
                        "title": "m1_en_t",
                        "desc": "m1_en_d",
                        "obs": "m1_en_o",
                        "help": "m1_en_h",
                        "importanceOfMilestone": "",
                    },
                    "fr": {
                        "title": "m1_fr_t",
                        "desc": "m1_fr_d",
                        "obs": "m1_fr_o",
                        "help": "m1_fr_h",
                        "importanceOfMilestone": "",
                    },
                },
                "images": [{"id": 1}, {"id": 2}],
            },
        ],
    }


@pytest.fixture
def milestone_group_admin1():
    return {
        "id": 1,
        "order": 2,
        "text": {
            "de": {
                "group_id": 1,
                "desc": "g1_de_d",
                "title": "g1_de_t",
                "lang_id": "de",
            },
            "en": {
                "group_id": 1,
                "desc": "g1_en_d",
                "title": "g1_en_t",
                "lang_id": "en",
            },
            "fr": {
                "group_id": 1,
                "desc": "g1_fr_d",
                "title": "g1_fr_t",
                "lang_id": "fr",
            },
        },
        "milestones": [
            {
                "group_id": 1,
                "order": 11,
                "id": 3,
                "name": "m3",
                "expected_age_months": 18,
                "expected_age_delta": 8,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m3_de_o",
                        "help": "m3_de_h",
                        "importanceOfMilestone": "",
                        "title": "m3_de_t",
                        "desc": "m3_de_d",
                        "milestone_id": 3,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m3_en_o",
                        "help": "m3_en_h",
                        "importanceOfMilestone": "",
                        "title": "m3_en_t",
                        "desc": "m3_en_d",
                        "milestone_id": 3,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m3_fr_o",
                        "help": "m3_fr_h",
                        "importanceOfMilestone": "",
                        "title": "m3_fr_t",
                        "desc": "m3_fr_d",
                        "milestone_id": 3,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 1,
                "order": 12,
                "id": 2,
                "name": "m2",
                "expected_age_months": 12,
                "expected_age_delta": 6,
                "images": [
                    {
                        "id": 3,
                        "milestone_id": 2,
                    }
                ],
                "text": {
                    "de": {
                        "obs": "m2_de_o",
                        "help": "m2_de_h",
                        "importanceOfMilestone": "",
                        "title": "m2_de_t",
                        "desc": "m2_de_d",
                        "milestone_id": 2,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m2_en_o",
                        "help": "m2_en_h",
                        "importanceOfMilestone": "",
                        "title": "m2_en_t",
                        "desc": "m2_en_d",
                        "milestone_id": 2,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m2_fr_o",
                        "help": "m2_fr_h",
                        "importanceOfMilestone": "",
                        "title": "m2_fr_t",
                        "desc": "m2_fr_d",
                        "milestone_id": 2,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 1,
                "order": 13,
                "id": 1,
                "name": "m1",
                "expected_age_months": 6,
                "expected_age_delta": 4,
                "images": [
                    {
                        "id": 1,
                        "milestone_id": 1,
                    },
                    {
                        "id": 2,
                        "milestone_id": 1,
                    },
                ],
                "text": {
                    "de": {
                        "obs": "m1_de_o",
                        "help": "m1_de_h",
                        "importanceOfMilestone": "",
                        "title": "m1_de_t",
                        "desc": "m1_de_d",
                        "milestone_id": 1,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m1_en_o",
                        "help": "m1_en_h",
                        "importanceOfMilestone": "",
                        "title": "m1_en_t",
                        "desc": "m1_en_d",
                        "milestone_id": 1,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m1_fr_o",
                        "help": "m1_fr_h",
                        "importanceOfMilestone": "",
                        "title": "m1_fr_t",
                        "desc": "m1_fr_d",
                        "milestone_id": 1,
                        "lang_id": "fr",
                    },
                },
            },
        ],
    }


@pytest.fixture
def milestone_group2():
    return {
        "id": 2,
        "text": {
            "de": {"title": "g1_de_t", "desc": "g1_de_d"},
            "en": {"title": "g1_en_t", "desc": "g1_en_d"},
            "fr": {"title": "g1_fr_t", "desc": "g1_fr_d"},
        },
        "milestones": [
            {
                "id": 4,
                "name": "m4",
                "images": [],
                "text": {
                    "de": {
                        "desc": "m4_de_d",
                        "title": "m4_de_t",
                        "obs": "m4_de_o",
                        "help": "m4_de_h",
                        "importanceOfMilestone": "",
                    },
                    "en": {
                        "desc": "m4_en_d",
                        "title": "m4_en_t",
                        "obs": "m4_en_o",
                        "help": "m4_en_h",
                        "importanceOfMilestone": "",
                    },
                    "fr": {
                        "desc": "m4_fr_d",
                        "title": "m4_fr_t",
                        "obs": "m4_fr_o",
                        "help": "m4_fr_h",
                        "importanceOfMilestone": "",
                    },
                },
            },
            {
                "id": 5,
                "name": "m5",
                "images": [],
                "text": {
                    "de": {
                        "desc": "m5_de_d",
                        "title": "m5_de_t",
                        "obs": "m5_de_o",
                        "help": "m5_de_h",
                        "importanceOfMilestone": "",
                    },
                    "en": {
                        "desc": "m5_en_d",
                        "title": "m5_en_t",
                        "obs": "m5_en_o",
                        "help": "m5_en_h",
                        "importanceOfMilestone": "",
                    },
                    "fr": {
                        "desc": "m5_fr_d",
                        "title": "m5_fr_t",
                        "obs": "m5_fr_o",
                        "help": "m5_fr_h",
                        "importanceOfMilestone": "",
                    },
                },
            },
        ],
    }


@pytest.fixture
def milestone_group_admin2():
    return {
        "id": 2,
        "order": 1,
        "text": {
            "de": {
                "group_id": 2,
                "desc": "g1_de_d",
                "title": "g1_de_t",
                "lang_id": "de",
            },
            "en": {
                "group_id": 2,
                "desc": "g1_en_d",
                "title": "g1_en_t",
                "lang_id": "en",
            },
            "fr": {
                "group_id": 2,
                "desc": "g1_fr_d",
                "title": "g1_fr_t",
                "lang_id": "fr",
            },
        },
        "milestones": [
            {
                "group_id": 2,
                "order": 4,
                "id": 4,
                "name": "m4",
                "expected_age_months": 24,
                "expected_age_delta": 10,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m4_de_o",
                        "help": "m4_de_h",
                        "importanceOfMilestone": "",
                        "title": "m4_de_t",
                        "desc": "m4_de_d",
                        "milestone_id": 4,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m4_en_o",
                        "help": "m4_en_h",
                        "importanceOfMilestone": "",
                        "title": "m4_en_t",
                        "desc": "m4_en_d",
                        "milestone_id": 4,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m4_fr_o",
                        "help": "m4_fr_h",
                        "importanceOfMilestone": "",
                        "title": "m4_fr_t",
                        "desc": "m4_fr_d",
                        "milestone_id": 4,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 2,
                "order": 5,
                "id": 5,
                "name": "m5",
                "expected_age_months": 30,
                "expected_age_delta": 12,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m5_de_o",
                        "help": "m5_de_h",
                        "importanceOfMilestone": "",
                        "title": "m5_de_t",
                        "desc": "m5_de_d",
                        "milestone_id": 5,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m5_en_o",
                        "help": "m5_en_h",
                        "importanceOfMilestone": "",
                        "title": "m5_en_t",
                        "desc": "m5_en_d",
                        "milestone_id": 5,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m5_fr_o",
                        "help": "m5_fr_h",
                        "importanceOfMilestone": "",
                        "title": "m5_fr_t",
                        "desc": "m5_fr_d",
                        "milestone_id": 5,
                        "lang_id": "fr",
                    },
                },
            },
        ],
    }
