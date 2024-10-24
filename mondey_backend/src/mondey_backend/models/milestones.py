from __future__ import annotations

import datetime

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


## MilestoneAgeGroup


class MilestoneAgeGroupBase(SQLModel):
    months_min: int
    months_max: int


class MilestoneAgeGroupCreate(MilestoneAgeGroupBase):
    pass


class MilestoneAgeGroup(MilestoneAgeGroupBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class MilestoneAgeGroupPublic(MilestoneAgeGroupBase):
    id: int


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
    age_group_id: int = Field(foreign_key="milestoneagegroup.id")
    order: int = 0
    text: Mapped[dict[str, MilestoneGroupText]] = dict_relationship(key="lang_id")
    milestones: Mapped[list[Milestone]] = back_populates("group")


class MilestoneGroupPublic(SQLModel):
    id: int
    text: dict[str, MilestoneGroupTextPublic] = {}
    milestones: list[MilestonePublic] = []


class MilestoneGroupAdmin(SQLModel):
    id: int
    age_group_id: int
    order: int
    text: dict[str, MilestoneGroupText] = {}
    milestones: list[MilestoneAdmin] = []


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
    group: MilestoneGroup | None = back_populates("milestones")
    text: Mapped[dict[str, MilestoneText]] = dict_relationship(key="lang_id")
    images: Mapped[list[MilestoneImage]] = back_populates("milestone")


class MilestonePublic(SQLModel):
    id: int
    text: dict[str, MilestoneTextPublic] = {}
    images: list[MilestoneImagePublic] = []


class MilestoneAdmin(SQLModel):
    id: int
    group_id: int
    order: int
    text: dict[str, MilestoneText] = {}
    images: list[MilestoneImage] = []


## MilestoneImage


class MilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(default=None, foreign_key="milestone.id")
    filename: str = ""
    approved: bool = False
    milestone: Milestone | None = back_populates("images")


class MilestoneImagePublic(SQLModel):
    filename: str
    approved: bool


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
    age_group_id: int = Field(foreign_key="milestoneagegroup.id")
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
    age_group_id: int
    created_at: datetime.datetime
    answers: dict[int, MilestoneAnswerPublic]
