"""Add dependent-question fields to user and child questions.

Adds ``depends_on_question_id`` and ``show_if_answer`` columns so that a
question can be conditionally shown depending on the answer to another
question of the same kind.

Revision ID: 20260724_01
Revises: 20260728_01
Create Date: 2026-07-24

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260724_01"
down_revision: str | Sequence[str] | None = "20260728_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def _add_dependent_columns(table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        # A new installation creates its tables during application startup.
        return
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if "depends_on_question_id" not in columns:
        op.add_column(
            table_name,
            sa.Column("depends_on_question_id", sa.Integer(), nullable=True),
        )
    if "show_if_answer" not in columns:
        op.add_column(
            table_name,
            sa.Column(
                "show_if_answer",
                sa.String(),
                nullable=False,
                server_default="",
            ),
        )


def upgrade_mondey() -> None:
    _add_dependent_columns("userquestion")
    _add_dependent_columns("childquestion")


def upgrade_users() -> None:
    pass
