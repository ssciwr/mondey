"""Store UTC timestamps, and interpret legacy creation timestamps as German time

Revision ID: 20261016_01
Revises: 20260730_01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261016_01"
down_revision: str | Sequence[str] | None = "20260730_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ("document", "milestoneanswersession", "milestoneagescorecollection")


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    inspector = sa.inspect(bind)
    for table_name in TABLES:
        if not inspector.has_table(table_name):
            continue
        columns = {
            column["name"]: column for column in inspector.get_columns(table_name)
        }
        if "created_at" not in columns:
            continue
        column_type = columns["created_at"]["type"]
        if column_type.timezone:
            continue
        op.alter_column(
            table_name,
            "created_at",
            existing_type=column_type,
            type_=sa.DateTime(timezone=True),
            postgresql_using="created_at AT TIME ZONE 'Europe/Berlin'",
        )


def upgrade_users() -> None:
    pass
