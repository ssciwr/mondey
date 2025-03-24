from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlmodel import Session

# This is the *test* database in import_data directory. Not the normal database, to avoid overwrites/issues
db_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./db/mondey.db",  # not the same as the normal DB
    # Make sure to refresh and connect to it, it will otherwise appear to be blank!
)  # will already have all the tables.
engine = create_engine(db_url)


def clear_all_milestones():
    pass


def get_import_test_session():
    with Session(engine) as session:
        yield session
