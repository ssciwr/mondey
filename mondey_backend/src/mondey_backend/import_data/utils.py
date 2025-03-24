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
        return session, engine


""" (For PR review) - Instead of this, I could add a ImportManager with a @contextamanger get_session, but basically,
I think it's useful for tests to just get_import_test_session (we know the strain on the DB won't be crazy with this
amount of data)

I can refactor it if useful, as I am not too happy just having functions exported from several files that are all
doing the same thing (importing), but at the same time I think it is pretty clear how they function for a one-off
import process. I think the individual tests for data existing, plus the full import to test each function can work
sequentially, should together confirm whether import works well or not.
"""
