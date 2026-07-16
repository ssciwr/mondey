from __future__ import annotations

import importlib.util
import pathlib

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def load_migration_module(filename: str):
    migration_path = (
        pathlib.Path(__file__).parents[1] / "alembic" / "versions" / filename
    )
    spec = importlib.util.spec_from_file_location(
        f"test_{migration_path.stem}", migration_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_milestone_age_curve_migration(tmp_path: pathlib.Path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'mondey-curve.db'}")
    metadata = sa.MetaData()
    score_collection = sa.Table(
        "milestoneagescorecollection",
        metadata,
        sa.Column("milestone_id", sa.Integer, primary_key=True),
        sa.Column("expected_age", sa.Integer, nullable=False),
        sa.Column("relevant_age_min", sa.Integer, nullable=False),
        sa.Column("relevant_age_max", sa.Integer, nullable=False),
    )
    metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(
            score_collection.insert().values(
                milestone_id=1,
                expected_age=12,
                relevant_age_min=6,
                relevant_age_max=18,
            )
        )
        migration = load_migration_module("20260717_01_add_milestone_age_curve.py")
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade_mondey()

        columns = {
            column["name"]
            for column in sa.inspect(connection).get_columns(
                "milestoneagescorecollection"
            )
        }
        assert {
            "curve_midpoint",
            "curve_steepness",
            "curve_fit_ok",
            "curve_n_answers",
        } <= columns
        migrated_values = connection.execute(
            sa.text(
                "SELECT curve_midpoint, curve_steepness, curve_fit_ok, "
                "curve_n_answers FROM milestoneagescorecollection "
                "WHERE milestone_id = 1"
            )
        ).one()
        assert migrated_values == (0.0, 0.0, 0, 0)


def test_answer_session_statistics_index_migration(tmp_path: pathlib.Path):
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'mondey.db'}")
    metadata = sa.MetaData()
    sa.Table(
        "milestoneanswersession",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("child_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("completed", sa.Boolean, nullable=False),
    )
    metadata.create_all(engine)

    with engine.begin() as connection:
        migration = load_migration_module(
            "20260717_02_add_answer_session_statistics_index.py"
        )
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade_mondey()

        indexes = {
            index["name"]: index
            for index in sa.inspect(connection).get_indexes("milestoneanswersession")
        }
        assert migration.INDEX_NAME in indexes
        assert indexes[migration.INDEX_NAME]["column_names"] == [
            "completed",
            "child_id",
            "created_at",
            "id",
        ]
