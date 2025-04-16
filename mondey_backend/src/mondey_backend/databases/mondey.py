from __future__ import annotations

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select
from sqlmodel.pool import StaticPool

from ..models.milestones import Language
from ..settings import app_settings

engine_path = (
    f"/{app_settings.DATABASE_PATH}/mondey.db" if app_settings.DATABASE_PATH else ""
)
engine = create_engine(
    f"sqlite://{engine_path}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_mondey_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # add "de" and "en" Languages if no languages are present in the database:
        if session.exec(select(Language)).first() is None:
            session.add(Language(id="de"))
            session.add(Language(id="en"))
            session.commit()
