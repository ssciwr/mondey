from __future__ import annotations

import datetime
import enum

from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlmodel import Enum
from sqlmodel import Field
from sqlmodel import SQLModel

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
        "group", order_by="asc(Milestone.order)", cascade="all, delete-orphan"
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
    name: str = ""
    answers: Mapped[list[MilestoneAnswer]] = back_populates(
        "milestone", cascade="all, delete-orphan"
    )


class MilestonePublic(SQLModel):
    id: int
    expected_age_months: int
    text: dict[str, MilestoneTextPublic]
    images: list[MilestoneImagePublic]
    name: str


class MilestoneAdmin(SQLModel):
    id: int
    group_id: int
    order: int
    expected_age_months: int
    text: dict[str, MilestoneText]
    images: list[MilestoneImage]
    name: str


## MilestoneImage
class MilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(default=None, foreign_key="milestone.id")
    milestone: Milestone = back_populates("images")


class MilestoneImagePublic(SQLModel):
    id: int


class SubmittedMilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(default=None, foreign_key="milestone.id")
    user_id: int


class SubmittedMilestoneImagePublic(SQLModel):
    id: int
    milestone_id: int
    user_id: int


## MilestoneAnswer


class MilestoneAnswerPublic(SQLModel):
    milestone_id: int
    answer: int


class MilestoneAnswerResponse(BaseModel):
    answer: MilestoneAnswerPublic
    session_completed: bool


class MilestoneAnswer(SQLModel, table=True):
    answer_session_id: int | None = Field(
        default=None, foreign_key="milestoneanswersession.id", primary_key=True
    )
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True
    )
    milestone_group_id: int = Field(default=None, foreign_key="milestonegroup.id")
    answer: int  # ranges from 0-3, where 0 is noch gar nichts and 3 is zuverlaessig, or -1 if not answered.
    milestone: Milestone = back_populates("answers")


class SuspiciousState(str, enum.Enum):
    """Enum for tracking suspicious state of an answer session.

    States:
    - admin_not_suspicious: Explicitly marked as not suspicious by admin, should not be overridden
    - not_suspicious: Not marked as suspicious by system (yet), can possibly be marked as susp. next time stats update
    - suspicious: Automatically marked as suspicious by system, may be overridden by admin
    - admin_suspicious: Explicitly marked as suspicious by admin, should not be overridden
    """

    admin_not_suspicious = "admin_not_suspicious"
    not_suspicious = "not_suspicious"
    suspicious = "suspicious"
    admin_suspicious = "admin_suspicious"


class MilestoneAnswerSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    child_id: int = Field(foreign_key="child.id", ondelete="CASCADE")
    user_id: int
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
    expired: bool
    completed: bool
    included_in_statistics: bool
    suspicious_state: str = Field(
        default=None,
        sa_column=Column(
            Enum(SuspiciousState),
            nullable=False,
        ),
    )

    answers: Mapped[dict[int, MilestoneAnswer]] = dict_relationship(key="milestone_id")


class MilestoneAnswerSessionPublic(SQLModel):
    id: int
    child_id: int
    created_at: datetime.datetime
    answers: dict[int, MilestoneAnswerPublic]


class MilestoneAnswerAnalysis(BaseModel):
    milestone_id: int
    answer: int
    avg_answer: float
    stddev_answer: float


class MilestoneAnswerSessionAnalysis(BaseModel):
    child_age: int
    rms: float
    answers: list[MilestoneAnswerAnalysis]


# models for statistics. README: Perhaps this could be made simpler if the data was stored in a database with array-column support. sqlite apparently doesnt have this: https://stackoverflow.com/questions/3005231/how-to-store-array-in-one-column-in-sqlite3, but postgres does: https://www.postgresql.org/docs/9.1/arrays.html
# will be returned to later. Issue no. 119
class MilestoneAgeScore(SQLModel, table=True):
    milestone_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="milestoneagescorecollection.milestone_id",
    )
    age: int = Field(primary_key=True)
    collection: MilestoneAgeScoreCollection = back_populates("scores")
    count: int
    avg_score: float
    stddev_score: float


class MilestoneAgeScoreCollection(SQLModel, table=True):
    milestone_id: int = Field(
        default=None, primary_key=True, foreign_key="milestone.id"
    )
    expected_age: int
    scores: Mapped[list[MilestoneAgeScore]] = back_populates("collection")
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class MilestoneAgeScoreCollectionPublic(SQLModel):
    milestone_id: int
    expected_age: int
    scores: list[MilestoneAgeScore]


class MilestoneGroupAgeScore(SQLModel, table=True):
    age: int | None = Field(default=None, primary_key=True)
    milestone_group_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="milestonegroupagescorecollection.milestone_group_id",
    )
    collection: MilestoneGroupAgeScoreCollection = back_populates("scores")
    count: int
    avg_score: float
    stddev_score: float


class MilestoneGroupAgeScoreCollection(SQLModel, table=True):
    milestone_group_id: int = Field(
        default=None, primary_key=True, foreign_key="milestonegroup.id"
    )
    scores: Mapped[list[MilestoneGroupAgeScore]] = back_populates("collection")
