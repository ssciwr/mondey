from __future__ import annotations

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import attribute_keyed_dict
from sqlalchemy.orm import relationship
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel


class UserQuestionTextBase(SQLModel):
    question: str = ""
    options_json: str = ""


class UserQuestionText(UserQuestionTextBase, table=True):
    user_question_id: int | None = Field(
        default=None, foreign_key="userquestion.id", primary_key=True
    )
    lang_id: int | None = Field(
        default=None, foreign_key="language.id", primary_key=True
    )
    options: str = ""


class UserQuestionTextPublic(UserQuestionTextBase):
    pass


class UserQuestion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order: int = 0
    input: str = "text"
    options: str = ""
    text: Mapped[dict[int, UserQuestionText]] = Relationship(
        sa_relationship=relationship(
            collection_class=attribute_keyed_dict("lang_id"),
            cascade="all, delete-orphan",
        )
    )


class UserQuestionPublic(SQLModel):
    id: int
    input: str
    text: dict[int, UserQuestionTextPublic] = {}


class UserQuestionAdmin(SQLModel):
    id: int
    order: int
    input: str
    options: str
    text: dict[int, UserQuestionText] = {}
