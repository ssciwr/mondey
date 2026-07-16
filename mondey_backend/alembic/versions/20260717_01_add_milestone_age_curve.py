"""Store fitted milestone age-curve parameters.

Revision ID: 20260717_01
Revises: 20260715_01
Create Date: 2026-07-17

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260717_01"
down_revision: str | Sequence[str] | None = "20260715_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "milestoneagescorecollection"
    if not inspector.has_table(table_name):
        # A new installation creates its tables during application startup.
        return

    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    columns = {
        "curve_midpoint": sa.Column(
            "curve_midpoint", sa.Float(), nullable=False, server_default=sa.text("0")
        ),
        "curve_steepness": sa.Column(
            "curve_steepness", sa.Float(), nullable=False, server_default=sa.text("0")
        ),
        "curve_fit_ok": sa.Column(
            "curve_fit_ok", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        "curve_n_answers": sa.Column(
            "curve_n_answers", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
    }
    for column_name, column in columns.items():
        if column_name not in existing_columns:
            op.add_column(table_name, column)


def upgrade_users() -> None:
    pass
