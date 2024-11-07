from __future__ import annotations

from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import select

from ..models.milestones import Language
from ..models.questions import ChildQuestion
from ..models.questions import ChildQuestionText
from ..settings import app_settings

engine = create_engine(
    f"sqlite:///{app_settings.DATABASE_PATH}/milestones.db",
    connect_args={"check_same_thread": False},
)


def create_database():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # add "de" and "en" Languages if no languages are present in the database:
        if session.exec(select(Language)).first() is None:
            session.add(Language(id="de"))
            session.add(Language(id="en"))
            session.commit()

        if session.exec(select(ChildQuestion)).first() is None:
            session.add(
                ChildQuestion(
                    id=1,
                    order=1,
                    component="textarea",
                    type="text",
                    text={
                        "de": ChildQuestionText(
                            child_question_id=1,
                            lang_id="de",
                            question="Name des Kindes?",
                            options="",
                        ),
                        "en": ChildQuestionText(
                            child_question_id=1,
                            lang_id="en",
                            question="Child'Name?",
                            options="",
                        ),
                    },
                )
            )
            session.add(
                ChildQuestion(
                    id=2,
                    order=2,
                    component="date",
                    type="input",
                    text={
                        "de": ChildQuestionText(
                            child_question_id=2,
                            lang_id="de",
                            question="Geburtstag des Kindes?",
                            options="",
                        ),
                        "en": ChildQuestionText(
                            child_question_id=2,
                            lang_id="en",
                            question="Child's birthday?",
                            options="",
                        ),
                    },
                )
            )
            session.add(
                ChildQuestion(
                    id=3,
                    order=3,
                    component="textarea",
                    type="text",
                    text={
                        "de": ChildQuestionText(
                            child_question_id=3,
                            lang_id="de",
                            question="Bemerkungen",
                            options="",
                        ),
                        "en": ChildQuestionText(
                            child_question_id=3,
                            lang_id="en",
                            question="Remarks",
                            options="",
                        ),
                    },
                )
            )
            session.add(
                ChildQuestion(
                    id=4,
                    order=4,
                    component="fileupload",
                    type="input",
                    text={
                        "de": ChildQuestionText(
                            child_question_id=4,
                            lang_id="de",
                            question="Bild hochladen",
                            options="",
                        ),
                        "en": ChildQuestionText(
                            child_question_id=4,
                            lang_id="en",
                            question="Upload image",
                            options="",
                        ),
                    },
                )
            )
            session.commit()
