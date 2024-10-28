from __future__ import annotations

import datetime
import pathlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mondey_backend import settings
from mondey_backend.dependencies import current_active_researcher
from mondey_backend.dependencies import current_active_superuser
from mondey_backend.dependencies import current_active_user
from mondey_backend.dependencies import get_session
from mondey_backend.main import create_app
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAgeGroup
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupText
from mondey_backend.models.milestones import MilestoneImage
from mondey_backend.models.milestones import MilestoneText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.users import UserRead
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture(scope="session")
def static_dir(tmp_path_factory: pytest.TempPathFactory):
    # use the same single temporary directory in all tests for static files
    static_dir = tmp_path_factory.mktemp("static")
    # add some milestone image files
    for filename in ["m1.jpg", "m2.jpg", "m3.jpg"]:
        with (static_dir / filename).open("w") as f:
            f.write(filename)
    return static_dir


@pytest.fixture(scope="session")
def private_dir(tmp_path_factory: pytest.TempPathFactory):
    # use the same single temporary directory in all tests for private files
    private_dir = tmp_path_factory.mktemp("private")
    children_dir = private_dir / "children"
    children_dir.mkdir()
    # add some child image files
    for filename in ["2.jpg", "3.jpg"]:
        with (children_dir / filename).open("w") as f:
            f.write(filename)
    return private_dir


@pytest.fixture
def session():
    # use a new in-memory SQLite database for each test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    SQLModel.metadata.create_all(engine)
    # add some test data
    with Session(engine) as session:
        # add 3 languages
        lang_ids = ["de", "en", "fr"]
        for lang_id in lang_ids:
            session.add(Language(id=lang_id))
        # add two milestone age groups
        session.add(MilestoneAgeGroup(months_min=0, months_max=36))
        session.add(MilestoneAgeGroup(months_min=36, months_max=72))
        # add a milestone group with 3 milestones
        session.add(MilestoneGroup(order=2, age_group_id=1))
        for lang_id in lang_ids:
            lbl = f"g1_{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=1, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )
        for milestone_id in [1, 2, 3]:
            session.add(Milestone(order=0, group_id=1))
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
                    )
                )
        # add a second milestone group with 2 milestones
        session.add(MilestoneGroup(order=1, age_group_id=1))
        for lang_id in lang_ids:
            lbl = f"g1_{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=2, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )
        for milestone_id in [4, 5]:
            session.add(Milestone(order=0, group_id=2))
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
                    )
                )
        # add the milestone images that were created in the static directory
        session.add(MilestoneImage(milestone_id=1, filename="m1.jpg", approved=True))
        session.add(MilestoneImage(milestone_id=1, filename="m2.jpg", approved=True))
        session.add(MilestoneImage(milestone_id=2, filename="m3.jpg", approved=True))
        session.commit()
        # add a ~1 yr old child for user 1
        today = datetime.datetime.today()
        session.add(
            Child(
                user_id=1,
                name="child1",
                birth_year=today.year - 1,
                birth_month=today.month,
                has_image=False,
            )
        )
        # add a ~4 yr old child for user 2
        session.add(
            Child(
                user_id=1,
                name="child2",
                birth_year=today.year - 4,
                birth_month=12,
                has_image=True,
            )
        )
        # add a ~5 year old child for user 3
        session.add(
            Child(
                user_id=3,
                name="child3",
                birth_year=today.year - 5,
                birth_month=7,
                has_image=True,
            )
        )
        # add an (expired) milestone answer session for child 1 / user 1 with no answers
        session.add(
            MilestoneAnswerSession(
                child_id=1,
                user_id=1,
                age_group_id=1,
                created_at=datetime.datetime(today.year - 1, 1, 1),
            )
        )
        # add another (current) milestone answer session for child 1 / user 1 with 2 answers
        session.add(
            MilestoneAnswerSession(
                child_id=1, user_id=1, age_group_id=1, created_at=today
            )
        )
        # add two milestone answers
        session.add(MilestoneAnswer(answer_session_id=2, milestone_id=1, answer=0))
        session.add(MilestoneAnswer(answer_session_id=2, milestone_id=2, answer=3))
        # add an (expired) milestone answer session for child 3 / user 3 with 1 answer
        session.add(
            MilestoneAnswerSession(
                child_id=3,
                user_id=3,
                age_group_id=2,
                created_at=datetime.datetime(today.year - 1, 1, 1),
            )
        )
        session.add(MilestoneAnswer(answer_session_id=3, milestone_id=7, answer=2))

        # add user answers for user 1
        session.add(
            UserAnswer(
                id=1,
                question_id=1,
                user_id=1,
                answer="lorem ipsum",
                additional_answer=None,
            )
        )
        session.add(
            UserAnswer(
                id=2,
                question_id=2,
                user_id=1,
                answer="other",
                additional_answer="dolor sit",
            )
        )

        yield session


@pytest.fixture
def active_admin_user():
    return UserRead(
        id=3,
        email="admin@mondey.de",
        is_active=True,
        is_superuser=True,
        is_researcher=False,
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
        is_verified=True,
    )


@pytest.fixture
def active_user():
    return UserRead(
        id=1,
        email="user@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        is_verified=True,
    )


@pytest.fixture
def second_active_user():
    return UserRead(
        id=2,
        email="user2@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        is_verified=True,
    )


@pytest.fixture(scope="session")
def app(static_dir: pathlib.Path, private_dir: pathlib.Path):
    settings.app_settings.STATIC_FILES_PATH = str(static_dir)
    settings.app_settings.PRIVATE_FILES_PATH = str(private_dir)
    app = create_app()
    return app


@pytest.fixture
def public_client(app: FastAPI, session: Session):
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_client(app: FastAPI, session: Session, active_user: UserRead):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[current_active_user] = lambda: active_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def second_user_client(app: FastAPI, session: Session, second_active_user: UserRead):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[current_active_user] = lambda: second_active_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def research_client(
    app: FastAPI,
    session: Session,
    active_research_user: UserRead,
):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[current_active_user] = lambda: active_research_user
    app.dependency_overrides[current_active_researcher] = lambda: active_research_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(
    app: FastAPI,
    session: Session,
    active_admin_user: UserRead,
):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[current_active_user] = lambda: active_admin_user
    app.dependency_overrides[current_active_superuser] = lambda: active_admin_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def jpg_file(tmp_path: pathlib.Path):
    jpg_path = tmp_path / "test.jpg"
    with jpg_path.open("w") as f:
        f.write("test")
    return jpg_path


@pytest.fixture
def children():
    today = datetime.datetime.today()
    return [
        {
            "birth_month": today.month,
            "birth_year": today.year - 1,
            "id": 1,
            "name": "child1",
            "has_image": False,
        },
        {
            "birth_month": 12,
            "birth_year": today.year - 4,
            "id": 2,
            "name": "child2",
            "has_image": True,
        },
        {
            "birth_month": 7,
            "birth_year": today.year - 5,
            "id": 3,
            "name": "child3",
            "has_image": True,
        },
    ]


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
                "id": 1,
                "text": {
                    "de": {
                        "title": "m1_de_t",
                        "desc": "m1_de_d",
                        "obs": "m1_de_o",
                        "help": "m1_de_h",
                    },
                    "en": {
                        "title": "m1_en_t",
                        "desc": "m1_en_d",
                        "obs": "m1_en_o",
                        "help": "m1_en_h",
                    },
                    "fr": {
                        "title": "m1_fr_t",
                        "desc": "m1_fr_d",
                        "obs": "m1_fr_o",
                        "help": "m1_fr_h",
                    },
                },
                "images": [
                    {"filename": "m1.jpg", "approved": True},
                    {"filename": "m2.jpg", "approved": True},
                ],
            },
            {
                "id": 2,
                "text": {
                    "de": {
                        "title": "m2_de_t",
                        "desc": "m2_de_d",
                        "obs": "m2_de_o",
                        "help": "m2_de_h",
                    },
                    "en": {
                        "title": "m2_en_t",
                        "desc": "m2_en_d",
                        "obs": "m2_en_o",
                        "help": "m2_en_h",
                    },
                    "fr": {
                        "title": "m2_fr_t",
                        "desc": "m2_fr_d",
                        "obs": "m2_fr_o",
                        "help": "m2_fr_h",
                    },
                },
                "images": [{"filename": "m3.jpg", "approved": True}],
            },
            {
                "id": 3,
                "text": {
                    "de": {
                        "title": "m3_de_t",
                        "desc": "m3_de_d",
                        "obs": "m3_de_o",
                        "help": "m3_de_h",
                    },
                    "en": {
                        "title": "m3_en_t",
                        "desc": "m3_en_d",
                        "obs": "m3_en_o",
                        "help": "m3_en_h",
                    },
                    "fr": {
                        "title": "m3_fr_t",
                        "desc": "m3_fr_d",
                        "obs": "m3_fr_o",
                        "help": "m3_fr_h",
                    },
                },
                "images": [],
            },
        ],
    }


@pytest.fixture
def milestone_group_admin1():
    return {
        "id": 1,
        "age_group_id": 1,
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
                "order": 0,
                "id": 1,
                "images": [
                    {
                        "id": 1,
                        "milestone_id": 1,
                        "filename": "m1.jpg",
                        "approved": True,
                    },
                    {
                        "id": 2,
                        "milestone_id": 1,
                        "filename": "m2.jpg",
                        "approved": True,
                    },
                ],
                "text": {
                    "de": {
                        "obs": "m1_de_o",
                        "help": "m1_de_h",
                        "title": "m1_de_t",
                        "desc": "m1_de_d",
                        "milestone_id": 1,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m1_en_o",
                        "help": "m1_en_h",
                        "title": "m1_en_t",
                        "desc": "m1_en_d",
                        "milestone_id": 1,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m1_fr_o",
                        "help": "m1_fr_h",
                        "title": "m1_fr_t",
                        "desc": "m1_fr_d",
                        "milestone_id": 1,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 1,
                "order": 0,
                "id": 2,
                "images": [
                    {
                        "id": 3,
                        "milestone_id": 2,
                        "filename": "m3.jpg",
                        "approved": True,
                    }
                ],
                "text": {
                    "de": {
                        "obs": "m2_de_o",
                        "help": "m2_de_h",
                        "title": "m2_de_t",
                        "desc": "m2_de_d",
                        "milestone_id": 2,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m2_en_o",
                        "help": "m2_en_h",
                        "title": "m2_en_t",
                        "desc": "m2_en_d",
                        "milestone_id": 2,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m2_fr_o",
                        "help": "m2_fr_h",
                        "title": "m2_fr_t",
                        "desc": "m2_fr_d",
                        "milestone_id": 2,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 1,
                "order": 0,
                "id": 3,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m3_de_o",
                        "help": "m3_de_h",
                        "title": "m3_de_t",
                        "desc": "m3_de_d",
                        "milestone_id": 3,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m3_en_o",
                        "help": "m3_en_h",
                        "title": "m3_en_t",
                        "desc": "m3_en_d",
                        "milestone_id": 3,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m3_fr_o",
                        "help": "m3_fr_h",
                        "title": "m3_fr_t",
                        "desc": "m3_fr_d",
                        "milestone_id": 3,
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
                "images": [],
                "text": {
                    "de": {
                        "desc": "m4_de_d",
                        "title": "m4_de_t",
                        "obs": "m4_de_o",
                        "help": "m4_de_h",
                    },
                    "en": {
                        "desc": "m4_en_d",
                        "title": "m4_en_t",
                        "obs": "m4_en_o",
                        "help": "m4_en_h",
                    },
                    "fr": {
                        "desc": "m4_fr_d",
                        "title": "m4_fr_t",
                        "obs": "m4_fr_o",
                        "help": "m4_fr_h",
                    },
                },
            },
            {
                "id": 5,
                "images": [],
                "text": {
                    "de": {
                        "desc": "m5_de_d",
                        "title": "m5_de_t",
                        "obs": "m5_de_o",
                        "help": "m5_de_h",
                    },
                    "en": {
                        "desc": "m5_en_d",
                        "title": "m5_en_t",
                        "obs": "m5_en_o",
                        "help": "m5_en_h",
                    },
                    "fr": {
                        "desc": "m5_fr_d",
                        "title": "m5_fr_t",
                        "obs": "m5_fr_o",
                        "help": "m5_fr_h",
                    },
                },
            },
        ],
    }


@pytest.fixture
def milestone_group_admin2():
    return {
        "id": 2,
        "age_group_id": 1,
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
                "order": 0,
                "id": 4,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m4_de_o",
                        "help": "m4_de_h",
                        "title": "m4_de_t",
                        "desc": "m4_de_d",
                        "milestone_id": 4,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m4_en_o",
                        "help": "m4_en_h",
                        "title": "m4_en_t",
                        "desc": "m4_en_d",
                        "milestone_id": 4,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m4_fr_o",
                        "help": "m4_fr_h",
                        "title": "m4_fr_t",
                        "desc": "m4_fr_d",
                        "milestone_id": 4,
                        "lang_id": "fr",
                    },
                },
            },
            {
                "group_id": 2,
                "order": 0,
                "id": 5,
                "images": [],
                "text": {
                    "de": {
                        "obs": "m5_de_o",
                        "help": "m5_de_h",
                        "title": "m5_de_t",
                        "desc": "m5_de_d",
                        "milestone_id": 5,
                        "lang_id": "de",
                    },
                    "en": {
                        "obs": "m5_en_o",
                        "help": "m5_en_h",
                        "title": "m5_en_t",
                        "desc": "m5_en_d",
                        "milestone_id": 5,
                        "lang_id": "en",
                    },
                    "fr": {
                        "obs": "m5_fr_o",
                        "help": "m5_fr_h",
                        "title": "m5_fr_t",
                        "desc": "m5_fr_d",
                        "milestone_id": 5,
                        "lang_id": "fr",
                    },
                },
            },
        ],
    }
