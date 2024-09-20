from __future__ import annotations

from sqlmodel import SQLModel
from sqlmodel import create_engine

from ..settings import app_settings

engine = create_engine(
    f"sqlite:///{app_settings.MILESTONE_DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)


def create_database():
    SQLModel.metadata.create_all(engine)
