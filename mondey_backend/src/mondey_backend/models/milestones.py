from __future__ import annotations

import datetime
import enum

import numpy as np
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
from .utils import list_relationship

# Note: models with relationships are defined in the same file to
# avoid the weird hacks required to make relationships work across files


class Language(SQLModel, table=True):
    id: str = fixed_length_string_field(max_length=2, index=True, primary_key=True)


class AdminSettings(SQLModel, table=True):
    """Admin settings for controlling application behavior. Single row table. For now, all are for feedback visiblity"""

    id: int = Field(default=1, primary_key=True)  # Always 1 - single row table
    hide_milestone_feedback: bool = Field(default=False)
    hide_milestone_group_feedback: bool = Field(default=False)
    hide_all_feedback: bool = Field(default=False)


class AdminSettingsPublic(SQLModel):
    hide_milestone_feedback: bool
    hide_milestone_group_feedback: bool
    hide_all_feedback: bool


class AdminSettingsUpdate(SQLModel):
    hide_milestone_feedback: bool | None = None
    hide_milestone_group_feedback: bool | None = None
    hide_all_feedback: bool | None = None


## MilestoneGroupText
class MilestoneGroupTextBase(SQLModel):
    title: str = ""
    desc: str = ""


class MilestoneGroupText(MilestoneGroupTextBase, table=True):
    group_id: int | None = Field(
        default=None,
        foreign_key="milestonegroup.id",
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
    milestones: Mapped[list[Milestone]] = list_relationship(
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
    importance: str = ""


class MilestoneText(MilestoneTextBase, table=True):
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True, ondelete="CASCADE"
    )
    lang_id: str | None = fixed_length_string_field(
        max_length=2,
        default=None,
        foreign_key="language.id",
        primary_key=True,
        ondelete="CASCADE",
    )


class MilestoneTextPublic(MilestoneTextBase):
    pass


## Milestone
class Milestone(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int | None = Field(
        default=None, foreign_key="milestonegroup.id", ondelete="CASCADE"
    )
    order: int = 0
    expected_age_months: int = 12
    expected_age_delta: int = 6
    group: MilestoneGroup = back_populates("milestones")
    text: Mapped[dict[str, MilestoneText]] = dict_relationship(key="lang_id")
    images: Mapped[list[MilestoneImage]] = list_relationship("milestone")
    name: str = ""
    answers: Mapped[list[MilestoneAnswer]] = list_relationship("milestone")


class MilestonePublic(SQLModel):
    id: int
    text: dict[str, MilestoneTextPublic]
    images: list[MilestoneImagePublic]
    name: str


class MilestoneAdmin(SQLModel):
    id: int
    group_id: int
    order: int
    expected_age_months: int
    expected_age_delta: int
    text: dict[str, MilestoneText]
    images: list[MilestoneImage]
    name: str


## MilestoneImage
class MilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", ondelete="CASCADE"
    )
    milestone: Milestone = back_populates("images")


class MilestoneImagePublic(SQLModel):
    id: int


class SubmittedMilestoneImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", ondelete="CASCADE"
    )
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
        default=None,
        foreign_key="milestoneanswersession.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    milestone_id: int | None = Field(
        default=None, foreign_key="milestone.id", primary_key=True, ondelete="CASCADE"
    )
    milestone_group_id: int = Field(
        default=None, foreign_key="milestonegroup.id", ondelete="CASCADE"
    )
    answer: int  # ranges from 0-3, where 0 is noch gar nichts and 3 is zuverlaessig, or -1 if not answered.
    milestone: Milestone = back_populates("answers")


class SuspiciousState(str, enum.Enum):
    """Enum for tracking suspicious state of an answer session.

    States:
    - admin_not_suspicious: Explicitly marked as not suspicious by admin, cannot be overridden by system
    - not_suspicious: Marked as not suspicious by system, may be overridden by admin
    - suspicious: Marked as suspicious by system, may be overridden by admin
    - admin_suspicious: Explicitly marked as suspicious by admin, cannot be overridden by system
    - unknown: Not yet analyzed default, will be marked as suspicious or not_suspicious by system next time stats update
    """

    admin_not_suspicious = "admin_not_suspicious"
    not_suspicious = "not_suspicious"
    suspicious = "suspicious"
    admin_suspicious = "admin_suspicious"
    unknown = "unknown"


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


class MilestoneAgeScore(SQLModel, table=True):
    milestone_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="milestoneagescorecollection.milestone_id",
        ondelete="CASCADE",
    )
    age: int = Field(primary_key=True)
    collection: MilestoneAgeScoreCollection = back_populates("scores")
    c0: int
    c1: int
    c2: int
    c3: int

    @property
    def count(self) -> int:
        return self.c0 + self.c1 + self.c2 + self.c3

    @property
    def mean(self) -> float:
        n = self.count
        if n == 0:
            return 0.0
        return (self.c1 + 2 * self.c2 + 3 * self.c3) / self.count

    @property
    def stddev(self) -> float:
        """Calculate the sample standard deviation of the scores.
        where sample stddev = sqrt((E[x^2] - E[x]^2) * n/(n-1))
        """
        n = self.count
        if n < 2:
            return 0.0
        m = self.mean
        m2 = (self.c1 + 4 * self.c2 + 9 * self.c3) / n
        return np.sqrt((m2 - m * m) * (n / (n - 1)))


class MilestoneAgeScoreCollection(SQLModel, table=True):
    milestone_id: int = Field(
        default=None, primary_key=True, foreign_key="milestone.id", ondelete="CASCADE"
    )
    expected_age: int
    expected_age_delta: int
    scores: Mapped[list[MilestoneAgeScore]] = list_relationship("collection")
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class MilestoneAgeScoreCollectionPublic(SQLModel):
    milestone_id: int
    expected_age: int
    expected_age_delta: int
    scores: list[MilestoneAgeScore]


class MilestoneGroupAgeScore(SQLModel, table=True):
    age: int | None = Field(default=None, primary_key=True)
    milestone_group_id: int | None = Field(
        default=None,
        primary_key=True,
        foreign_key="milestonegroupagescorecollection.milestone_group_id",
        ondelete="CASCADE",
    )
    collection: MilestoneGroupAgeScoreCollection = back_populates("scores")
    count: int
    sum_score: float
    sum_squaredscore: float

    @property
    def mean(self) -> float:
        return self.sum_score / self.count

    @property
    def stddev(self) -> float:
        """Calculate the sample standard deviation of the scores.
        where sample stddev = sqrt((E[x^2] - E[x]^2) * n/(n-1))
        """
        n = self.count
        if n < 2:
            return 0.0
        m = self.mean
        m2 = self.sum_squaredscore / self.count
        return np.sqrt((m2 - m * m) * (n / (n - 1)))


class MilestoneGroupAgeScoreCollection(SQLModel, table=True):
    milestone_group_id: int = Field(
        default=None,
        primary_key=True,
        foreign_key="milestonegroup.id",
        ondelete="CASCADE",
    )
    scores: Mapped[list[MilestoneGroupAgeScore]] = list_relationship("collection")
