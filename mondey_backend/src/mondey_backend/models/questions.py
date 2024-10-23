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


# Answers to user questions. Internal model and 'public' model exposed to the forntend app


class UserAnswer(SQLModel, table=True):
    """
    Internal model for user answers.

    Parameters
    ----------
    UserAnswerBase : Base type for all UserAnswer models

    table : bool, True
        Makes sure this is created as a table in the database, by default True
    """

    # remove id, make user_id a primary key and quesiton_id a primary key and then work with those.
    user_id: int = Field(default=None, primary_key=True)
    question_id: int = Field(
        default=None, primary_key=True, foreign_key="userquestion.id"
    )
    answer: str
    # flag that tells the frontend if the answer has been given via an  additional text field => won´t be correctly displayed otherwise
    non_standard: bool


class UserAnswerPublic(SQLModel):
    """
    External data model for UserAnswers

    Parameters
    ----------
    SQLModel : Pydantic model  basic sqlmodel pydantic type
    """

    answer: str
    question_id: int
    non_standard: bool
