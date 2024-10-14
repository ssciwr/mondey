from __future__ import annotations

import pathlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool

from mondey_backend import settings
from mondey_backend.dependencies import current_active_researcher
from mondey_backend.dependencies import current_active_superuser
from mondey_backend.dependencies import current_active_user
from mondey_backend.dependencies import get_session
from mondey_backend.main import create_app
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupText
from mondey_backend.models.milestones import MilestoneImage
from mondey_backend.models.milestones import MilestoneText
from mondey_backend.models.users import UserRead


@pytest.fixture(scope="session")
def static_dir(tmp_path_factory: pytest.TempPathFactory):
    # use the same single temporary directory in all tests for static files
    static_dir = tmp_path_factory.mktemp("static")
    # add some milestone image files
    for filename in ["m1.jpg", "m2.jpg", "m3.jpg"]:
        with (static_dir / filename).open("w") as f:
            f.write(filename)
    return static_dir


@pytest.fixture
def session(static_dir: pathlib.Path):
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
        for lang in ["de", "en", "fr"]:
            session.add(Language(lang=lang))
        lang_ids = [1, 2, 3]
        # add a milestone group with 3 milestones
        session.add(MilestoneGroup(order=2))
        for lang_id in lang_ids:
            lbl = f"g1_l{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=1, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )
        for milestone_id in [1, 2, 3]:
            session.add(Milestone(order=0, group_id=1))
            for lang_id in lang_ids:
                lbl = f"m{milestone_id}_l{lang_id}"
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
        session.add(MilestoneGroup(order=1))
        for lang_id in lang_ids:
            lbl = f"g1_l{lang_id}"
            session.add(
                MilestoneGroupText(
                    group_id=2, lang_id=lang_id, title=f"{lbl}_t", desc=f"{lbl}_d"
                )
            )
        for milestone_id in [4, 5]:
            session.add(Milestone(order=0, group_id=2))
            for lang_id in lang_ids:
                lbl = f"m{milestone_id}_l{lang_id}"
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
        yield session


@pytest.fixture
def active_admin_user():
    UserRead(
        id=3,
        email="admin@mondey.de",
        is_active=True,
        is_superuser=True,
        is_researcher=False,
        is_verified=True,
    )


@pytest.fixture
def active_research_user():
    UserRead(
        id=2,
        email="research@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=True,
        is_verified=True,
    )


@pytest.fixture
def active_user():
    UserRead(
        id=1,
        email="user@mondey.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        is_verified=True,
    )


@pytest.fixture(scope="session")
def app(static_dir: pathlib.Path):
    settings.app_settings.STATIC_FILES_PATH = str(static_dir)
    app = create_app()
    return app


@pytest.fixture
def user_client(app: FastAPI, session: Session, active_user: UserRead):
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[current_active_user] = lambda: active_user
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
def milestone_group1():
    return {
        "id": 1,
        "text": {
            "1": {"title": "g1_l1_t", "desc": "g1_l1_d"},
            "2": {"title": "g1_l2_t", "desc": "g1_l2_d"},
            "3": {"title": "g1_l3_t", "desc": "g1_l3_d"},
        },
        "milestones": [
            {
                "id": 1,
                "text": {
                    "1": {
                        "title": "m1_l1_t",
                        "desc": "m1_l1_d",
                        "obs": "m1_l1_o",
                        "help": "m1_l1_h",
                    },
                    "2": {
                        "title": "m1_l2_t",
                        "desc": "m1_l2_d",
                        "obs": "m1_l2_o",
                        "help": "m1_l2_h",
                    },
                    "3": {
                        "title": "m1_l3_t",
                        "desc": "m1_l3_d",
                        "obs": "m1_l3_o",
                        "help": "m1_l3_h",
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
                    "1": {
                        "title": "m2_l1_t",
                        "desc": "m2_l1_d",
                        "obs": "m2_l1_o",
                        "help": "m2_l1_h",
                    },
                    "2": {
                        "title": "m2_l2_t",
                        "desc": "m2_l2_d",
                        "obs": "m2_l2_o",
                        "help": "m2_l2_h",
                    },
                    "3": {
                        "title": "m2_l3_t",
                        "desc": "m2_l3_d",
                        "obs": "m2_l3_o",
                        "help": "m2_l3_h",
                    },
                },
                "images": [{"filename": "m3.jpg", "approved": True}],
            },
            {
                "id": 3,
                "text": {
                    "1": {
                        "title": "m3_l1_t",
                        "desc": "m3_l1_d",
                        "obs": "m3_l1_o",
                        "help": "m3_l1_h",
                    },
                    "2": {
                        "title": "m3_l2_t",
                        "desc": "m3_l2_d",
                        "obs": "m3_l2_o",
                        "help": "m3_l2_h",
                    },
                    "3": {
                        "title": "m3_l3_t",
                        "desc": "m3_l3_d",
                        "obs": "m3_l3_o",
                        "help": "m3_l3_h",
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
        "order": 2,
        "text": {
            "1": {"group_id": 1, "desc": "g1_l1_d", "title": "g1_l1_t", "lang_id": 1},
            "2": {"group_id": 1, "desc": "g1_l2_d", "title": "g1_l2_t", "lang_id": 2},
            "3": {"group_id": 1, "desc": "g1_l3_d", "title": "g1_l3_t", "lang_id": 3},
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
                    "1": {
                        "obs": "m1_l1_o",
                        "help": "m1_l1_h",
                        "title": "m1_l1_t",
                        "desc": "m1_l1_d",
                        "milestone_id": 1,
                        "lang_id": 1,
                    },
                    "2": {
                        "obs": "m1_l2_o",
                        "help": "m1_l2_h",
                        "title": "m1_l2_t",
                        "desc": "m1_l2_d",
                        "milestone_id": 1,
                        "lang_id": 2,
                    },
                    "3": {
                        "obs": "m1_l3_o",
                        "help": "m1_l3_h",
                        "title": "m1_l3_t",
                        "desc": "m1_l3_d",
                        "milestone_id": 1,
                        "lang_id": 3,
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
                    "1": {
                        "obs": "m2_l1_o",
                        "help": "m2_l1_h",
                        "title": "m2_l1_t",
                        "desc": "m2_l1_d",
                        "milestone_id": 2,
                        "lang_id": 1,
                    },
                    "2": {
                        "obs": "m2_l2_o",
                        "help": "m2_l2_h",
                        "title": "m2_l2_t",
                        "desc": "m2_l2_d",
                        "milestone_id": 2,
                        "lang_id": 2,
                    },
                    "3": {
                        "obs": "m2_l3_o",
                        "help": "m2_l3_h",
                        "title": "m2_l3_t",
                        "desc": "m2_l3_d",
                        "milestone_id": 2,
                        "lang_id": 3,
                    },
                },
            },
            {
                "group_id": 1,
                "order": 0,
                "id": 3,
                "images": [],
                "text": {
                    "1": {
                        "obs": "m3_l1_o",
                        "help": "m3_l1_h",
                        "title": "m3_l1_t",
                        "desc": "m3_l1_d",
                        "milestone_id": 3,
                        "lang_id": 1,
                    },
                    "2": {
                        "obs": "m3_l2_o",
                        "help": "m3_l2_h",
                        "title": "m3_l2_t",
                        "desc": "m3_l2_d",
                        "milestone_id": 3,
                        "lang_id": 2,
                    },
                    "3": {
                        "obs": "m3_l3_o",
                        "help": "m3_l3_h",
                        "title": "m3_l3_t",
                        "desc": "m3_l3_d",
                        "milestone_id": 3,
                        "lang_id": 3,
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
            "1": {"title": "g1_l1_t", "desc": "g1_l1_d"},
            "2": {"title": "g1_l2_t", "desc": "g1_l2_d"},
            "3": {"title": "g1_l3_t", "desc": "g1_l3_d"},
        },
        "milestones": [
            {
                "id": 4,
                "images": [],
                "text": {
                    "1": {
                        "desc": "m4_l1_d",
                        "title": "m4_l1_t",
                        "obs": "m4_l1_o",
                        "help": "m4_l1_h",
                    },
                    "2": {
                        "desc": "m4_l2_d",
                        "title": "m4_l2_t",
                        "obs": "m4_l2_o",
                        "help": "m4_l2_h",
                    },
                    "3": {
                        "desc": "m4_l3_d",
                        "title": "m4_l3_t",
                        "obs": "m4_l3_o",
                        "help": "m4_l3_h",
                    },
                },
            },
            {
                "id": 5,
                "images": [],
                "text": {
                    "1": {
                        "desc": "m5_l1_d",
                        "title": "m5_l1_t",
                        "obs": "m5_l1_o",
                        "help": "m5_l1_h",
                    },
                    "2": {
                        "desc": "m5_l2_d",
                        "title": "m5_l2_t",
                        "obs": "m5_l2_o",
                        "help": "m5_l2_h",
                    },
                    "3": {
                        "desc": "m5_l3_d",
                        "title": "m5_l3_t",
                        "obs": "m5_l3_o",
                        "help": "m5_l3_h",
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
            "1": {"group_id": 2, "desc": "g1_l1_d", "title": "g1_l1_t", "lang_id": 1},
            "2": {"group_id": 2, "desc": "g1_l2_d", "title": "g1_l2_t", "lang_id": 2},
            "3": {"group_id": 2, "desc": "g1_l3_d", "title": "g1_l3_t", "lang_id": 3},
        },
        "milestones": [
            {
                "group_id": 2,
                "order": 0,
                "id": 4,
                "images": [],
                "text": {
                    "1": {
                        "obs": "m4_l1_o",
                        "help": "m4_l1_h",
                        "title": "m4_l1_t",
                        "desc": "m4_l1_d",
                        "milestone_id": 4,
                        "lang_id": 1,
                    },
                    "2": {
                        "obs": "m4_l2_o",
                        "help": "m4_l2_h",
                        "title": "m4_l2_t",
                        "desc": "m4_l2_d",
                        "milestone_id": 4,
                        "lang_id": 2,
                    },
                    "3": {
                        "obs": "m4_l3_o",
                        "help": "m4_l3_h",
                        "title": "m4_l3_t",
                        "desc": "m4_l3_d",
                        "milestone_id": 4,
                        "lang_id": 3,
                    },
                },
            },
            {
                "group_id": 2,
                "order": 0,
                "id": 5,
                "images": [],
                "text": {
                    "1": {
                        "obs": "m5_l1_o",
                        "help": "m5_l1_h",
                        "title": "m5_l1_t",
                        "desc": "m5_l1_d",
                        "milestone_id": 5,
                        "lang_id": 1,
                    },
                    "2": {
                        "obs": "m5_l2_o",
                        "help": "m5_l2_h",
                        "title": "m5_l2_t",
                        "desc": "m5_l2_d",
                        "milestone_id": 5,
                        "lang_id": 2,
                    },
                    "3": {
                        "obs": "m5_l3_o",
                        "help": "m5_l3_h",
                        "title": "m5_l3_t",
                        "desc": "m5_l3_d",
                        "milestone_id": 5,
                        "lang_id": 3,
                    },
                },
            },
        ],
    }
