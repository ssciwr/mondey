import importlib.util
import os
from datetime import UTC
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

MIGRATION = (
    Path(__file__).parents[1] / "alembic/versions/20261016_01_use_utc_timestamps.py"
)


@pytest.fixture
def migration_connection():
    database_url = os.getenv("MONDEY_TEST_POSTGRES_URL")
    if database_url is None:
        pytest.skip("Set MONDEY_TEST_POSTGRES_URL to exercise PostgreSQL migrations")
    engine = sa.create_engine(database_url)
    assert engine.dialect.name == "postgresql"
    with engine.connect() as connection, connection.begin():
        # Isolate test tables from any existing application data. Rollback
        # removes the schema and all test data when this fixture exits.
        schema = f"timezone_test_{uuid4().hex}"
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
        yield connection
        connection.rollback()
    engine.dispose()


def load_migration(connection, monkeypatch):
    spec = importlib.util.spec_from_file_location("timezone_migration", MIGRATION)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    monkeypatch.setattr(
        migration, "op", Operations(MigrationContext.configure(connection))
    )
    return migration


def test_legacy_berlin_timestamps_become_utc(migration_connection, monkeypatch):
    connection = migration_connection
    migration = load_migration(connection, monkeypatch)
    values = [
        ("2026-01-15 12:00:00", datetime(2026, 1, 15, 11, tzinfo=UTC)),
        ("2026-07-15 12:00:00", datetime(2026, 7, 15, 10, tzinfo=UTC)),
        ("2026-03-29 02:30:00", datetime(2026, 3, 29, 1, 30, tzinfo=UTC)),
        ("2026-10-25 02:30:00", datetime(2026, 10, 25, 1, 30, tzinfo=UTC)),
    ]
    for table in migration.TABLES:
        connection.exec_driver_sql(
            f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, created_at TIMESTAMP)"
        )
        for index, (local_time, _) in enumerate(values):
            connection.execute(
                sa.text(f"INSERT INTO {table} VALUES (:id, :created_at)"),
                {"id": index, "created_at": local_time},
            )
    connection.exec_driver_sql(
        "CREATE TABLE calendarevent (id INTEGER PRIMARY KEY, event_date TIMESTAMP)"
    )
    connection.exec_driver_sql(
        "INSERT INTO calendarevent VALUES (1, '2026-07-15 00:00:00')"
    )
    calendar_before = connection.exec_driver_sql("SELECT * FROM calendarevent").all()
    # Conversion must not depend on the connection's timezone.
    connection.exec_driver_sql("SET LOCAL TIME ZONE 'America/New_York'")
    migration.upgrade("mondey")
    for table in migration.TABLES:
        actual = (
            connection.exec_driver_sql(f"SELECT created_at FROM {table} ORDER BY id")
            .scalars()
            .all()
        )
        assert actual == [utc_time for _, utc_time in values]
    assert (
        calendar_before
        == connection.exec_driver_sql("SELECT * FROM calendarevent").all()
    )


def test_new_installation_without_tables(migration_connection, monkeypatch):
    migration = load_migration(migration_connection, monkeypatch)
    migration.upgrade("mondey")
    migration.upgrade("users")


def test_existing_aware_postgres_column_is_not_reinterpreted(
    migration_connection, monkeypatch
):
    connection = migration_connection
    connection.exec_driver_sql(
        "CREATE TABLE document (id INTEGER PRIMARY KEY, created_at TIMESTAMPTZ)"
    )
    connection.exec_driver_sql(
        "INSERT INTO document VALUES (1, '2026-07-15 12:00:00+00')"
    )
    migration = load_migration(connection, monkeypatch)
    migration.upgrade("mondey")
    migration.upgrade("mondey")
    assert connection.exec_driver_sql(
        "SELECT created_at FROM document"
    ).scalar_one() == (datetime(2026, 7, 15, 12, tzinfo=UTC))
