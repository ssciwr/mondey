import datetime

import pytest
from sqlmodel import Session
from sqlmodel import create_engine
from sqlmodel import select
from sqlmodel import text

from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswerSession

DATABASE_TIMESTAMP_MODELS = [
    (MilestoneAgeScoreCollection, {"milestone_id": 1}),
    (
        MilestoneAnswerSession,
        {
            "child_id": 1,
            "user_id": 1,
            "expired": False,
            "completed": False,
            "included_in_statistics": False,
            "suspicious_state": "unknown",
        },
    ),
]


@pytest.mark.parametrize(("model", "values"), DATABASE_TIMESTAMP_MODELS)
@pytest.mark.parametrize(
    "explicit_timestamp", [None, datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)]
)
def test_creation_timestamp_defaults_and_overrides(model, values, explicit_timestamp):
    engine = create_engine("sqlite://")
    model.__table__.create(engine)
    with Session(engine) as session:
        before = datetime.datetime.now(datetime.UTC)
        record = model(
            **values,
            **({"created_at": explicit_timestamp} if explicit_timestamp else {}),
        )
        assert record.created_at.tzinfo is not None
        if explicit_timestamp is None:
            assert before <= record.created_at <= datetime.datetime.now(datetime.UTC)
        else:
            assert record.created_at == explicit_timestamp
        created_at = record.created_at
        session.add(record)
        session.commit()
        session.refresh(record)
        assert record.created_at.utcoffset() == datetime.timedelta()
        assert record.created_at == created_at
    engine.dispose()


@pytest.mark.parametrize(("model", "values"), DATABASE_TIMESTAMP_MODELS)
def test_creation_timestamp_database_fallback(model, values):
    engine = create_engine("sqlite://")
    model.__table__.create(engine)
    # Raw SQL bypasses the Python defaults, so only the database can supply created_at.
    insert_values = model(**values).model_dump(
        exclude={"created_at"}, exclude_none=True
    )
    columns = ", ".join(insert_values)
    parameters = ", ".join(f":{column}" for column in insert_values)
    with Session(engine) as session:
        session.execute(
            text(
                f"INSERT INTO {model.__tablename__} ({columns}) VALUES ({parameters})"
            ),
            insert_values,
        )
        session.commit()
        record = session.exec(select(model)).one()
        assert record.created_at.utcoffset() == datetime.timedelta()
        assert abs(datetime.datetime.now(datetime.UTC) - record.created_at) < (
            datetime.timedelta(seconds=5)
        )
    engine.dispose()
