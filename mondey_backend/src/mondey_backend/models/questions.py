from __future__ import annotations

from sqlalchemy.orm import Mapped
from sqlmodel import Field
from sqlmodel import SQLModel

from .utils import dict_relationship
from .utils import fixed_length_string_field


class UserQuestionTextBase(SQLModel):
    question: str = ""
    options_json: str = ""


class UserQuestionText(UserQuestionTextBase, table=True):
    user_question_id: int | None = Field(
        default=None, foreign_key="userquestion.id", primary_key=True
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2, default=None, foreign_key="language.id", primary_key=True
    )
    options: str = ""


class UserQuestionTextPublic(UserQuestionTextBase):
    pass


class UserQuestion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order: int = 0
    component: str = "select"
    type: str = "text"
    options: str = ""
    text: Mapped[dict[str, UserQuestionText]] = dict_relationship(key="lang_id")
    additional_option: str = ""


class UserQuestionPublic(SQLModel):
    id: int
    component: str = "select"
    type: str = "text"
    text: dict[str, UserQuestionTextPublic] = {}
    additional_option: str = ""


class UserQuestionAdmin(SQLModel):
    id: int
    order: int
    component: str = "select"
    type: str = "text"
    options: str
    text: dict[str, UserQuestionText] = {}
    additional_option: str = ""


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

    user_id: int = Field(default=None, primary_key=True)
    question_id: int = Field(
        default=None, primary_key=True, foreign_key="userquestion.id"
    )
    answer: str
    # flag that tells the frontend if the answer has been given via an  additional text field => won´t be correctly displayed otherwise
    additional_answer: str | None


class UserAnswerPublic(SQLModel):
    """
    External data model for UserAnswers

    Parameters
    ----------
    SQLModel : Pydantic model  basic sqlmodel pydantic type
    """

    answer: str
    question_id: int
    additional_answer: str | None
