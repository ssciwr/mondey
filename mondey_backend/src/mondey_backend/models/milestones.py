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


## age interval for milestones
class AgeInterval(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    lower_limit: int
    upper_limit: int


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
    age_interval: int = Field(default=None, foreign_key="ageinterval.id")


class MilestonePublic(SQLModel):
    id: int
    expected_age_months: int
    text: dict[str, MilestoneTextPublic]
    images: list[MilestoneImagePublic]
    age_interval: int


class MilestoneAdmin(SQLModel):
    id: int
    group_id: int
    order: int
    expected_age_months: int
    text: dict[str, MilestoneText]
    images: list[MilestoneImage]
    age_interval: int = Field(default=None, foreign_key="ageinterval.id")


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


class MilestoneAnswer(SQLModel, table=True):
    answer_session_id: int | None = Field(
        default=None, foreign_key="milestoneanswersession.id", primary_key=True
    )
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True
    )
    milestone_group_id: int = Field(default=None, foreign_key="milestonegroup.id")
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


class MilestoneAgeScore(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    collection_id: int | None = Field(
        default=None, foreign_key="milestoneagescorecollection.id"
    )
    collection: MilestoneAgeScoreCollection = back_populates("scores")
    count: int
    avg_score: float
    stddev_score: float
    age_months: int
    expected_score: float


class MilestoneAgeScorePublic(SQLModel):
    def __init__(
        self, count=0, avg_score=0, stddev_score=0, age_months=0, expected_score=0
    ):
        self.count = count
        self.avg_score = avg_score
        self.stddev_score = stddev_score
        self.age_months = age_months
        self.expected_score = expected_score

    count: int
    avg_score: float
    stddev_score: float
    age_months: int
    expected_score: float


class MilestoneAgeScoreCollection(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    milestone_id: int = Field(default=None, foreign_key="milestone.id")
    expected_age: int
    scores: Mapped[list[MilestoneAgeScore]] = back_populates("collection")
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class MilestoneAgeScoreCollectionPublic(SQLModel):
    def __init__(self, milestone_id=0, expected_age=0, scores=None, created_at=None):
        self.milestone_id = milestone_id
        self.expected_age = expected_age
        self.scores = scores or []
        self.created_at = created_at or datetime.datetime.now()

    milestone_id: int
    expected_age: int
    scores: list[MilestoneAgeScorePublic]
    created_at: datetime.datetime


class MilestoneGroupAgeScore(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    collection_id: int | None = Field(
        default=None, foreign_key="milestonegroupagescorecollection.id"
    )
    collection: MilestoneGroupAgeScoreCollection = back_populates("scores")
    count: int
    avg_score: float
    stddev_score: float
    age_months: int
    milestonegroup_id: int = Field(
        default=None, primary_key=True, foreign_key="milestonegroup.id"
    )


class MilestoneGroupAgeScorePublic(SQLModel):
    def __init__(
        self, count=0, avg_score=0, stddev_score=0, age_months=0, milestonegroup_id=0
    ):
        self.count = count
        self.avg_score = avg_score
        self.stddev_score = stddev_score
        self.age_months = age_months
        self.milestonegroup_id = milestonegroup_id

    count: int
    avg_score: float
    stddev_score: float
    age_months: int
    milestonegroup_id: int


class MilestoneGroupAgeScoreCollection(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    milestonegroup_id: int = Field(default=None, foreign_key="milestonegroup.id")
    scores: Mapped[list[MilestoneGroupAgeScore]] = back_populates("collection")
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class MilestoneGroupAgeScoreCollectionPublic(SQLModel):
    def __init__(self, milestonegroup_id=0, scores=None, created_at=None):
        self.milestonegroup_id = milestonegroup_id
        self.scores = scores or []
        self.created_at = created_at or datetime.datetime.now()

    id: int
    milestonegroup_id: int
    scores: list[MilestoneGroupAgeScorePublic]
    created_at: datetime.datetime
