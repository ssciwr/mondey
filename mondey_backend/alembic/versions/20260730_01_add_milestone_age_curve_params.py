"""Make the milestone ages configurable and drop the heuristic fallback.

Adds the parameters that control how a milestone's expected age and relevant age
range are derived from its fitted age curve to the admin settings, and drops those
ages from the score collection: they are now derived from the stored curve at the
configured parameters whenever they are asked for, rather than being stored. The
stored values came from the heuristic that no longer exists anyway.

Revision ID: 20260730_01
Revises: 20260729_02
Create Date: 2026-07-30

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from mondey_backend.models.milestones import DEFAULT_MEAN_ANSWER_ACHIEVED
from mondey_backend.models.milestones import DEFAULT_MEAN_ANSWER_RELEVANT_MAX
from mondey_backend.models.milestones import DEFAULT_MEAN_ANSWER_RELEVANT_MIN
from mondey_backend.models.milestones import DEFAULT_MIN_RELEVANT_AGE_MARGIN_MONTHS

revision: str = "20260730_01"
down_revision: str | Sequence[str] | None = "20260729_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("adminsettings"):
        # a new installation creates its tables during application startup
        existing_columns = {
            column["name"] for column in inspector.get_columns("adminsettings")
        }
        columns = {
            "mean_answer_achieved": sa.Column(
                "mean_answer_achieved",
                sa.Float(),
                nullable=False,
                server_default=sa.text(str(DEFAULT_MEAN_ANSWER_ACHIEVED)),
            ),
            "mean_answer_relevant_min": sa.Column(
                "mean_answer_relevant_min",
                sa.Float(),
                nullable=False,
                server_default=sa.text(str(DEFAULT_MEAN_ANSWER_RELEVANT_MIN)),
            ),
            "mean_answer_relevant_max": sa.Column(
                "mean_answer_relevant_max",
                sa.Float(),
                nullable=False,
                server_default=sa.text(str(DEFAULT_MEAN_ANSWER_RELEVANT_MAX)),
            ),
            "min_relevant_age_margin_months": sa.Column(
                "min_relevant_age_margin_months",
                sa.Integer(),
                nullable=False,
                server_default=sa.text(str(DEFAULT_MIN_RELEVANT_AGE_MARGIN_MONTHS)),
            ),
        }
        for column_name, column in columns.items():
            if column_name not in existing_columns:
                op.add_column("adminsettings", column)

    table_name = "milestoneagescorecollection"
    if not inspector.has_table(table_name):
        return
    # the expected age and relevant age range are no longer stored: they are derived
    # from the stored age curve at the configured parameters whenever they are asked
    # for, so that they cannot go stale with respect to the fit they came from
    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    age_columns = [
        column_name
        for column_name in ("expected_age", "relevant_age_min", "relevant_age_max")
        if column_name in existing_columns
    ]
    if age_columns:
        with op.batch_alter_table(table_name) as batch_op:
            for column_name in age_columns:
                batch_op.drop_column(column_name)


def upgrade_users() -> None:
    pass
