from __future__ import annotations

import tempfile

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select

from ..models.milestones import Language
from ..settings import app_settings

engine = create_engine(
    f"sqlite:///{app_settings.DATABASE_PATH if app_settings.DATABASE_PATH else tempfile.mkdtemp()}/mondey.db",
    connect_args={"check_same_thread": False},
)


def create_mondey_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # add "de" and "en" Languages if no languages are present in the database:
        if session.exec(select(Language)).first() is None:
            session.add(Language(id="de"))
            session.add(Language(id="en"))
            session.commit()
