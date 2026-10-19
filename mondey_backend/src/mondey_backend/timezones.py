from datetime import UTC
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

GERMAN_TIMEZONE = ZoneInfo("Europe/Berlin")


def german_time_to_utc(value: datetime) -> datetime:
    """Interpret timezone-free survey timestamps as German local time.

    Prefer standard time for ambiguous/nonexistent DST times, matching
    PostgreSQL's AT TIME ZONE conversion used by the database migration.
    """
    if value.tzinfo is None:
        first = value.replace(tzinfo=GERMAN_TIMEZONE, fold=0)
        second = value.replace(tzinfo=GERMAN_TIMEZONE, fold=1)
        value = min((first, second), key=lambda dt: dt.utcoffset() or timedelta())
    return value.astimezone(UTC)
