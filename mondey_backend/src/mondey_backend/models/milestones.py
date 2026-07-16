from __future__ import annotations

import datetime
import enum

import numpy as np
from pydantic import BaseModel
from pydantic import model_validator
from sqlalchemy import Column
from sqlalchemy import Index
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


# The mean answer at which a milestone is considered achieved. The answers are on a
# 0-3 scale, so 2.4 is 80% of the maximum.
DEFAULT_MEAN_ANSWER_ACHIEVED = 2.4
# The mean answers delimiting the age range over which a milestone is worth asking:
# from when a few children can do it until nearly all of them can.
DEFAULT_MEAN_ANSWER_RELEVANT_MIN = 0.3
DEFAULT_MEAN_ANSWER_RELEVANT_MAX = 2.7
# The smallest margin either side of the expected age that the relevant age range must
# cover. A steep curve crosses the two relevant thresholds within a couple of months,
# which would leave too narrow a window for a child to be asked about the milestone.
DEFAULT_MIN_RELEVANT_AGE_MARGIN_MONTHS = 2


class MilestoneAgeCurveParams(SQLModel):
    """
    How a milestone's expected age and relevant age range are derived from its fitted
    age curve, see `get_milestone_ages_from_curve`. The three thresholds are mean
    answers on the same 0-3 scale as the curve itself; each is converted to the age at
    which the curve reaches it. The margin only widens the relevant age range at the
    end, and does not affect the expected age.
    """

    # the thresholds have to stay strictly inside (0, 3): the curve only approaches 0
    # and 3 asymptotically, so the age at either of them is infinite
    mean_answer_achieved: float = Field(
        default=DEFAULT_MEAN_ANSWER_ACHIEVED, gt=0.0, lt=3.0
    )
    mean_answer_relevant_min: float = Field(
        default=DEFAULT_MEAN_ANSWER_RELEVANT_MIN, gt=0.0, lt=3.0
    )
    mean_answer_relevant_max: float = Field(
        default=DEFAULT_MEAN_ANSWER_RELEVANT_MAX, gt=0.0, lt=3.0
    )
    min_relevant_age_margin_months: int = Field(
        default=DEFAULT_MIN_RELEVANT_AGE_MARGIN_MONTHS, ge=0
    )

    @model_validator(mode="after")
    def achieved_threshold_inside_relevant_range(self) -> MilestoneAgeCurveParams:
        # the milestone is only asked about within its relevant age range, so the age at
        # which it is expected to be achieved has to lie inside that range
        if not (
            self.mean_answer_relevant_min
            <= self.mean_answer_achieved
            <= self.mean_answer_relevant_max
        ):
            raise ValueError(
                "mean_answer_achieved must lie between mean_answer_relevant_min "
                "and mean_answer_relevant_max"
            )
        return self


class AdminSettings(SQLModel, table=True):
    """Admin settings for controlling application behavior. Single row table."""

    id: int = Field(default=1, primary_key=True)  # Always 1 - single row table
    hide_milestone_feedback: bool = Field(default=False)
    hide_milestone_group_feedback: bool = Field(default=False)
    hide_all_feedback: bool = Field(default=False)
    # how the milestone ages are derived from the fitted age curves, see
    # MilestoneAgeCurveParams
    mean_answer_achieved: float = Field(default=DEFAULT_MEAN_ANSWER_ACHIEVED)
    mean_answer_relevant_min: float = Field(default=DEFAULT_MEAN_ANSWER_RELEVANT_MIN)
    mean_answer_relevant_max: float = Field(default=DEFAULT_MEAN_ANSWER_RELEVANT_MAX)
    min_relevant_age_margin_months: int = Field(
        default=DEFAULT_MIN_RELEVANT_AGE_MARGIN_MONTHS
    )

    def milestone_age_curve_params(self) -> MilestoneAgeCurveParams:
        return MilestoneAgeCurveParams(
            mean_answer_achieved=self.mean_answer_achieved,
            mean_answer_relevant_min=self.mean_answer_relevant_min,
            mean_answer_relevant_max=self.mean_answer_relevant_max,
            min_relevant_age_margin_months=self.min_relevant_age_margin_months,
        )


class AdminSettingsPublic(SQLModel):
    hide_milestone_feedback: bool
    hide_milestone_group_feedback: bool
    hide_all_feedback: bool
    mean_answer_achieved: float
    mean_answer_relevant_min: float
    mean_answer_relevant_max: float
    min_relevant_age_margin_months: int


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
    relevant_age_min: int = 6
    relevant_age_max: int = 18
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
    relevant_age_min: int
    relevant_age_max: int
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
    __table_args__ = (
        Index(
            "ix_milestoneanswersession_completed_child_created_id",
            "completed",
            "child_id",
            "created_at",
            "id",
        ),
    )

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
    milestone_title: dict[str, str]
    milestone_order: int
    milestone_group_id: int
    milestone_group_name: dict[str, str]
    milestone_group_order: int
    answer: int
    avg_answer: float
    stddev_answer: float


class ChildAnswerAnalysisFlag(BaseModel):
    question_id: int
    question: dict[str, str]
    answer: str
    additional_answer: str | None


class MilestoneAnswerSessionAnalysis(BaseModel):
    child_age: int
    rms: float
    answers: list[MilestoneAnswerAnalysis]
    child_answer_flags: list[ChildAnswerAnalysisFlag]


class StatisticsUpdateResult(BaseModel):
    """Result of a statistics recalculation, used to build a localized summary in the UI."""

    answer_sessions: int
    answers: int
    runtime_seconds: float


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
    # The fitted age curve for this milestone is defined by the midpoint and the steepness
    curve_midpoint: float = 0.0
    curve_steepness: float = 0.0
    curve_fit_ok: bool = False
    curve_n_answers: int = 0
    scores: Mapped[list[MilestoneAgeScore]] = list_relationship("collection")
    created_at: datetime.datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class MilestoneAgeScoreCollectionPublic(SQLModel):
    milestone_id: int
    # these three ages are derived from the curve if curve_fit_ok, otherwise None
    expected_age: int | None
    relevant_age_min: int | None
    relevant_age_max: int | None
    curve_midpoint: float
    curve_steepness: float
    curve_fit_ok: bool
    curve_n_answers: int
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
        if self.count == 0:
            # no answer session contributed a score for this milestone group and age
            return 0.0
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
        # rounding can make this expression slightly negative when the scores are all
        # (almost) identical, which would give a nan
        variance = max(m2 - m * m, 0.0)
        return float(np.sqrt(variance * (n / (n - 1))))


class MilestoneGroupAgeScoreCollection(SQLModel, table=True):
    milestone_group_id: int = Field(
        default=None,
        primary_key=True,
        foreign_key="milestonegroup.id",
        ondelete="CASCADE",
    )
    scores: Mapped[list[MilestoneGroupAgeScore]] = list_relationship("collection")
