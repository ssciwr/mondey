"""Add access-token activity timestamp.

Revision ID: 20260715_01
Revises:
Create Date: 2026-07-15

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260715_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    pass


def upgrade_users() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("accesstoken"):
        # A new installation creates its tables during application startup.
        return
    columns = {column["name"] for column in inspector.get_columns("accesstoken")}
    if "last_seen_at" in columns:
        return

    op.add_column(
        "accesstoken",
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(sa.text("UPDATE accesstoken SET last_seen_at = created_at"))
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("accesstoken") as batch_op:
            batch_op.alter_column(
                "last_seen_at",
                existing_type=sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.current_timestamp(),
            )
    else:
        op.alter_column(
            "accesstoken",
            "last_seen_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        )
