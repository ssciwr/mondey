from __future__ import annotations

import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Mapped
from sqlmodel import Field
from sqlmodel import SQLModel
from sqlmodel import text

from .utils import back_populates
from .utils import dict_relationship
from .utils import fixed_length_string_field

# Note: models with relationships are defined in the same file to
# avoid the weird hacks required to make relationships work across files


class Language(SQLModel, table=True):
    id: str = fixed_length_string_field(max_length=2, index=True, primary_key=True)


## MilestoneGroupText


class MilestoneGroupTextBase(SQLModel):
    title: str = ""
    desc: str = ""


class MilestoneGroupText(MilestoneGroupTextBase, table=True):
    group_id: int | None = Field(
        default=None, foreign_key="milestonegroup.id", primary_key=True
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2, default=None, foreign_key="language.id", primary_key=True
    )


class MilestoneGroupTextCreate(MilestoneGroupTextBase):
    group_id: int
    lang_id: str


class MilestoneGroupTextPublic(MilestoneGroupTextBase):
    pass


## MilestoneGroup


class MilestoneGroup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order: int = 0
    text: Mapped[dict[str, MilestoneGroupText]] = dict_relationship(key="lang_id")
    milestones: Mapped[list[Milestone]] = back_populates(
        "group", order_by="asc(Milestone.order)"
    )


class MilestoneGroupPublic(SQLModel):
    id: int
    text: dict[str, MilestoneGroupTextPublic]
    milestones: list[MilestonePublic]


class MilestoneGroupAdmin(SQLModel):
    id: int
    order: int
    text: dict[str, MilestoneGroupText]
    milestones: list[MilestoneAdmin]


## MilestoneText


class MilestoneTextBase(SQLModel):
    title: str = ""
    desc: str = ""
    obs: str = ""
    help: str = ""


class MilestoneText(MilestoneTextBase, table=True):
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2, default=None, foreign_key="language.id", primary_key=True
    )


class MilestoneTextPublic(MilestoneTextBase):
    pass


## Milestone


class Milestone(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int | None = Field(default=None, foreign_key="milestonegroup.id")
    order: int = 0
    expected_age_months: int = 12
    group: MilestoneGroup = back_populates("milestones")
    text: Mapped[dict[str, MilestoneText]] = dict_relationship(key="lang_id")
    images: Mapped[list[MilestoneImage]] = back_populates("milestone")


class MilestonePublic(SQLModel):
    id: int
    expected_age_months: int
    text: dict[str, MilestoneTextPublic]
    images: list[MilestoneImagePublic]


class MilestoneAdmin(SQLModel):
    id: int
    group_id: int
    order: int
    expected_age_months: int
    text: dict[str, MilestoneText]
    images: list[MilestoneImage]


## MilestoneImage


class MilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(default=None, foreign_key="milestone.id")
    milestone: Milestone = back_populates("images")


class MilestoneImagePublic(SQLModel):
    id: int


## MilestoneAnswer


class MilestoneAnswerPublic(SQLModel):
    milestone_id: int
    answer: int


class MilestoneAnswer(SQLModel, table=True):
    answer_session_id: int | None = Field(
        default=None, foreign_key="milestoneanswersession.id", primary_key=True
    )
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True
    )
    answer: int


class MilestoneAnswerSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    child_id: int = Field(foreign_key="child.id")
    user_id: int
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
    answers: Mapped[dict[int, MilestoneAnswer]] = dict_relationship(key="milestone_id")


class MilestoneAnswerSessionPublic(SQLModel):
    id: int
    child_id: int
    created_at: datetime.datetime
    answers: dict[int, MilestoneAnswerPublic]


class MilestoneAgeScore(BaseModel):
    milestone_id: int
    age_months: int
    avg_score: float
    sigma_score: float
    expected_score: float


class MilestoneAgeScores(BaseModel):
    scores: list[MilestoneAgeScore]
    expected_age: int


class MilestoneGroupAgeScore(BaseModel):
    age_months: int
    group_id: int | None
    avg_score: float
    sigma_score: float
