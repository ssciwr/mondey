"""Add the answer-session index used by chronological statistics processing.

Revision ID: 20260717_02
Revises: 20260717_01
Create Date: 2026-07-17

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260717_02"
down_revision: str | Sequence[str] | None = "20260717_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEX_NAME = "ix_milestoneanswersession_completed_child_created_id"


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "milestoneanswersession"
    if not inspector.has_table(table_name):
        # A new installation creates its tables during application startup.
        return
    index_names = {
        index["name"] for index in inspector.get_indexes(table_name) if index["name"]
    }
    if INDEX_NAME in index_names:
        return

    op.create_index(
        INDEX_NAME,
        table_name,
        ["completed", "child_id", "created_at", "id"],
        unique=False,
    )


def upgrade_users() -> None:
    pass
