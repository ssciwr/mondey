from __future__ import annotations

import datetime
import importlib.util
import pathlib

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def load_migration_module():
    migration_path = (
        pathlib.Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "20260715_01_add_access_token_last_seen.py"
    )
    spec = importlib.util.spec_from_file_location(
        "users_session_migration", migration_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_access_token_last_seen_migration(tmp_path: pathlib.Path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'users.db'}")
    metadata = sa.MetaData()
    access_token = sa.Table(
        "accesstoken",
        metadata,
        sa.Column("token", sa.String(43), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    metadata.create_all(engine)
    created_at = datetime.datetime(2026, 7, 15, 12, 0, tzinfo=datetime.UTC)
    with engine.begin() as connection:
        connection.execute(
            access_token.insert().values(token="existing-token", created_at=created_at)
        )

        migration = load_migration_module()
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade_users()

        inspector = sa.inspect(connection)
        assert "last_seen_at" in {
            column["name"] for column in inspector.get_columns("accesstoken")
        }
        last_seen_at = connection.scalar(
            sa.text(
                "SELECT last_seen_at FROM accesstoken WHERE token = 'existing-token'"
            )
        )
        assert last_seen_at == "2026-07-15 12:00:00.000000"
