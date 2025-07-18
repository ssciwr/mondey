from __future__ import annotations

from sqlalchemy.orm import Mapped
from sqlmodel import Field
from sqlmodel import SQLModel

from .utils import back_populates
from .utils import dict_relationship
from .utils import fixed_length_string_field
from .utils import list_relationship


# user questions
class QuestionTextBase(SQLModel):
    question: str = ""
    options_json: str = ""
    options: str = ""


class Question(SQLModel):
    order: int = 0
    component: str = "select"
    type: str = "text"
    options: str = ""
    additional_option: str = ""
    required: bool = False
    name: str = ""
    visibility: bool = False


class QuestionAdmin(Question):
    id: int


class QuestionTextPublic(QuestionTextBase):
    pass


class QuestionPublic(SQLModel):
    id: int
    component: str = "select"
    type: str = "text"
    text: dict[str, QuestionTextPublic] = {}
    additional_option: str = ""
    required: bool = False
    name: str = ""


class UserQuestionText(QuestionTextBase, table=True):
    user_question_id: int | None = Field(
        default=None,
        foreign_key="userquestion.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2,
        default=None,
        foreign_key="language.id",
        primary_key=True,
        ondelete="CASCADE",
    )


class UserQuestion(Question, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: Mapped[dict[str, UserQuestionText]] = dict_relationship(key="lang_id")
    answers: Mapped[list[UserAnswer]] = list_relationship("question")
    name: str = ""


class UserQuestionPublic(QuestionPublic):
    pass


class UserQuestionAdmin(QuestionAdmin):
    text: dict[str, UserQuestionText] = {}


# child questions


class ChildQuestionText(QuestionTextBase, table=True):
    child_question_id: int | None = Field(
        default=None,
        foreign_key="childquestion.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2,
        default=None,
        foreign_key="language.id",
        primary_key=True,
        ondelete="CASCADE",
    )


class ChildQuestion(Question, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: Mapped[dict[str, ChildQuestionText]] = dict_relationship(key="lang_id")
    answers: Mapped[list[ChildAnswer]] = list_relationship("question")
    name: str = ""


class ChildQuestionPublic(QuestionPublic):
    pass


class ChildQuestionAdmin(QuestionAdmin):
    text: dict[str, ChildQuestionText] = {}


# Answers to user questions. Internal model and 'public' model exposed to the frontend app
class AnswerBase(SQLModel):
    answer: str
    additional_answer: str | None


class AnswerPublicBase(AnswerBase):
    question_id: int


class UserAnswer(AnswerBase, table=True):
    user_id: int = Field(default=None, primary_key=True)
    question_id: int = Field(
        default=None,
        primary_key=True,
        foreign_key="userquestion.id",
        ondelete="CASCADE",
    )
    question: UserQuestion = back_populates("answers")


class UserAnswerPublic(AnswerPublicBase):
    pass


class ChildAnswer(AnswerBase, table=True):
    child_id: int = Field(default=None, primary_key=True)
    question_id: int = Field(
        default=None,
        primary_key=True,
        foreign_key="childquestion.id",
        ondelete="CASCADE",
    )
    question: ChildQuestion = back_populates("answers")


class ChildAnswerPublic(AnswerPublicBase):
    pass
