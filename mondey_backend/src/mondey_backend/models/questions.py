from __future__ import annotations

from sqlalchemy.orm import Mapped
from sqlmodel import Field
from sqlmodel import SQLModel

from .utils import dict_relationship
from .utils import fixed_length_string_field


# Base model classes for all questions text elements. Does not define any tables itself, but only the basic structure. These are not intended for direct use!
# Create derived models that implemenet proper key relations with descriptive names instead and use those in your endpoints
class QuestionTextBase(SQLModel):
    question: str = ""
    options_json: str = ""


class QuestionText(QuestionTextBase):
    question_id: int | None = Field(
        default=None, foreign_key="question.id", primary_key=True
    )

    lang_id: str | None = fixed_length_string_field(
        max_length=2, default=None, foreign_key="language.id", primary_key=True
    )
    options: str = ""


class Question(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    order: int = 0
    component: str = "select"
    type: str = "text"
    options: str = ""
    additional_option: str = ""


class QuestionTextPublic(QuestionTextBase):
    pass


class QuestionPublic(SQLModel):
    id: int
    component: str = "select"
    type: str = "text"
    text: dict[str, QuestionTextPublic] = {}
    additional_option: str = ""


class QuestionAdmin(SQLModel):
    id: int
    order: int
    component: str = "select"
    type: str = "text"
    options: str
    text: dict[str, QuestionText] = {}
    additional_option: str = ""


# User Question classes
class UserQuestionText(QuestionText, table=True):
    question_id: int | None = Field(
        default=None, foreign_key="userquestion.id", primary_key=True
    )


class ChildQuestionText(QuestionText, table=True):
    question_id: int | None = Field(
        default=None, foreign_key="childquestion.id", primary_key=True
    )


class UserQuestion(Question, table=True):
    text: Mapped[dict[str, UserQuestionText]] = dict_relationship(key="lang_id")


class UserQuestionPublic(QuestionPublic):
    pass


class UserQuestionAdmin(QuestionAdmin):
    text: Mapped[dict[str, UserQuestionText]] = dict_relationship(key="lang_id")


# Child question classes
class ChildQuestion(Question, table=True):
    text: Mapped[dict[str, ChildQuestionText]] = dict_relationship(key="lang_id")


class ChildQuestionPublic(QuestionPublic):
    pass


class ChildQuestionAdmin(QuestionAdmin):
    pass


class Answer(SQLModel):
    """
    Base Answer model for all internal data that holds answers to questions.

    Parameters
    ----------
    SQLModel: Makes this into a pydantic model for an SQL table entry.
    """

    user_id: int = Field(default=None, primary_key=True)
    question_id: int = Field(
        default=None, primary_key=True, foreign_key="userquestion.id"
    )
    answer: str
    additional_answer: str | None


class UserAnswer(Answer, table=True):
    """
    Internal model for UserAnswer with the same content as the base `Answer` type.

    Parameters
    ----------
    Answer : Base Answer model for all internal data that holds answers to questions.
    table : bool, optional
        Makes this a SQL table
    """

    pass


class ChildAnswer(Answer, table=True):
    """
    Internal model for child answer data which adds the child ID.

    Parameters
    ----------
    AnswerPublic : Basic Model for all Answers to questions in Mondey
    """

    child_id: int = Field(default=None, primary_key=True, foreign_key="child.id")


class AnswerPublic(SQLModel):
    """
    Internal data model for UserAnswers

    Parameters
    ----------
    SQLModel : Pydantic model  basic sqlmodel pydantic type
    """

    answer: str
    question_id: int
    additional_answer: str | None


class UserAnswerPublic(AnswerPublic):
    """
    Model for public user answer data with the same content as AnswerPublic

    Parameters
    ----------
    AnswerPublic : Basic Model for all Answers to questions in Mondey
    """

    pass


class ChildAnswerPublic(AnswerPublic):
    """
    Model for public child answer data which adds the child ID.

    Parameters
    ----------
    AnswerPublic : Basic Model for all Answers to questions in Mondey
    """

    child_id: int
