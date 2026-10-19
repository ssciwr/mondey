import datetime

import pytest
from sqlmodel import Session
from sqlmodel import create_engine

from mondey_backend.models.documents import Document
from mondey_backend.timezones import german_time_to_utc


@pytest.mark.parametrize(
    ("local_time", "utc_time"),
    [
        ("2026-01-15T12:00:00", "2026-01-15T11:00:00+00:00"),
        ("2026-07-15T12:00:00", "2026-07-15T10:00:00+00:00"),
        # Match PostgreSQL's standard-time choice for DST gaps and overlaps.
        ("2026-03-29T02:30:00", "2026-03-29T01:30:00+00:00"),
        ("2026-10-25T02:30:00", "2026-10-25T01:30:00+00:00"),
        ("2026-07-15T12:00:00+00:00", "2026-07-15T12:00:00+00:00"),
    ],
)
def test_german_survey_times_become_utc(local_time, utc_time):
    assert german_time_to_utc(datetime.datetime.fromisoformat(local_time)) == (
        datetime.datetime.fromisoformat(utc_time)
    )


def test_document_timestamp_round_trip_is_aware_utc():
    engine = create_engine("sqlite://")
    Document.__table__.create(engine)
    with Session(engine) as session:
        document = Document(title="Test", uploaded_by_user_id=1)
        session.add(document)
        session.commit()
        session.refresh(document)
        assert document.created_at.tzinfo is not None
        assert document.created_at.utcoffset() == datetime.timedelta()
        assert abs(datetime.datetime.now(datetime.UTC) - document.created_at) < (
            datetime.timedelta(seconds=5)
        )
    engine.dispose()
