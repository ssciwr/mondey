"""Remove user-submitted milestone images.

Users can no longer submit images for a milestone. This drops the table and
deletes the directory it referenced: submitted images that had not yet been
reviewed were stored in the publicly readable static files directory.

Note that approved images are not affected - approving a submitted image moved
it out of the submitted images directory (static/ms) into the directory for
published milestone images (static/m).

Revision ID: 20260728_01
Revises: 20260715_01
Create Date: 2026-07-28

"""

import logging
import pathlib
import shutil
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from mondey_backend.settings import app_settings

logger = logging.getLogger("alembic.runtime.migration")

revision: str = "20260728_01"
down_revision: str | Sequence[str] | None = "20260715_01"


def upgrade(engine_name: str) -> None:
    globals()[f"upgrade_{engine_name}"]()


def upgrade_mondey() -> None:
    # The image files live outside the database, in a directory that holds
    # nothing else, so remove it entirely. This also catches any files left
    # behind without a corresponding row in the table.
    submitted_images_dir = pathlib.Path(app_settings.STATIC_FILES_PATH) / "ms"
    if submitted_images_dir.is_dir():
        try:
            shutil.rmtree(submitted_images_dir)
        except OSError as e:
            # don't fail the migration: that would stop the backend from starting
            logger.warning(
                f"Could not remove submitted milestone images from {submitted_images_dir}: {e}. "
                "These files need to be deleted manually."
            )
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("submittedmilestoneimage"):
        # a new installation creates its tables during application startup,
        # which happens after this runs, so the table may not exist yet
        op.drop_table("submittedmilestoneimage")


def upgrade_users() -> None:
    pass
