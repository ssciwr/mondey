from __future__ import annotations

import pytest
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch):
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
