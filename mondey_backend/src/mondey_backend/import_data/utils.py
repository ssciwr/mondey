from __future__ import annotations

from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlmodel import Session

script_dir = Path(__file__).parent.parent.parent.parent.absolute()
database_file_path = script_dir / "src/mondey_backend/import_data/db/mondey.db"

# This is the *test* database in import_data directory. Not the normal database, to avoid overwrites/issues
db_url = "sqlite:////" + str(database_file_path)  # not the same as the normal DB
# Make sure to refresh and connect to it, it will otherwise appear to be blank!
engine = create_engine(db_url)


def clear_all_data():
    """Clear all data but do not delete the databases."""
    metadata = MetaData()
    metadata.reflect(bind=engine)

    with Session(engine) as session:
        session.execute("PRAGMA foreign_keys = OFF;")
        for table in metadata.sorted_tables:
            session.execute(f"DELETE FROM {table.name};")
        session.execute("PRAGMA foreign_keys = ON;")
        session.commit()


def get_import_test_session():
    with Session(engine) as session:
        return session, engine


# todo: Load the look up file into memory rather than keep opening/closing it...
# labelling_encoding_csv_path --> should be a dict of dicts e.g.
# 'FK01' --> { '1': '2010', '2': '2011' ...}


def get_lookup_mapped_value(column_key: str, column_lookup_ordinal: str) -> str:
    # returns the plaintext value of that column in the coding csv file which maps ordinal codes (numbers) to text values
    # todo: implement
    # if none is found (e.g. the column_lookup_ordinal is a freetext or empty, it returns what was called as the lookup
    # ordinal. This way if it is freetext, e.g. "Frankreich", then that gets kept as the answer.
    return ""


""" (For PR review) - Instead of this, I could add a ImportManager with a @contextamanger get_session, but basically,
I think it's useful for tests to just get_import_test_session (we know the strain on the DB won't be crazy with this
amount of data)

I can refactor it if useful, as I am not too happy just having functions exported from several files that are all
doing the same thing (importing), but at the same time I think it is pretty clear how they function for a one-off
import process. I think the individual tests for data existing, plus the full import to test each function can work
sequentially, should together confirm whether import works well or not.
"""
