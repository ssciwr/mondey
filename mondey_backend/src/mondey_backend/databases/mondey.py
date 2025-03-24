from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select

from ..models.milestones import Language
from ..settings import app_settings

engine = create_engine(
    f"sqlite:///{app_settings.DATABASE_PATH}/mondey.db",
    connect_args={"check_same_thread": False},
)


def create_mondey_db_and_tables_themselves(provided_engine: Engine) -> None:
    SQLModel.metadata.create_all(provided_engine)
    with Session(provided_engine) as session:
        # add "de" and "en" Languages if no languages are present in the database:
        if session.exec(select(Language)).first() is None:
            session.add(Language(id="de"))
            session.add(Language(id="en"))
            session.commit()


def create_mondey_db_and_tables(optional_engine: Engine | None = None) -> None:
    create_mondey_db_and_tables_themselves(
        engine if optional_engine is None else optional_engine
    )
