from sqlmodel import select

from mondey_backend.import_data.import_children_with_assigned_milestone_data import (
    map_children_milestones_data,
)
from mondey_backend.models.children import Child


def fake_data_csv():
    import csv
    from io import StringIO

    headers = [
        "CASE",
        "SERIAL",
        "REF",
        "QUESTNNR",
        "MODE",
        "STARTED",
        "FK01",
        "FK02",
        "DA03",
        "DE01_01",
    ]
    child_159_row = [159, 2671, 34, "Q1", "Online", "2024-03-28", 1, 9, 2, 3]
    child_208_row = [208, 3102, 57, "Q2", "Phone", "2024-03-29", 5, 6, 1, 2]

    # Create a StringIO to write CSV data
    f = StringIO()
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(headers)
    writer.writerow(child_159_row)
    writer.writerow(child_208_row)

    # Seek to the beginning of the file
    f.seek(0)

    return f


def test_duplicates_are_ignored_during_import(session):
    print("Importing.")
    import_session = session  # use per-test reset DB for this purpose.
    # clear_all_data(import_session)
    # todo: Use an inline CSV for the below.
    map_children_milestones_data(
        "unuseddata.csv", import_session, overwritten_csv=fake_data_csv()
    )
    child_id = 159
    child = import_session.execute(
        select(Child).where(Child.id == child_id)
    ).scalar_one_or_none()

    assert child.birth_year == 2024
    assert child.birth_month == 9

    children = import_session.exec(select(Child)).all()
    assert len(children) == 6
    print("Len children")
    print(len(children))
    print([child.id for child in children])
    # [1, 2, 3, 4, 159, 208]

    # check when reimporting exactly the same that duplicates get ignored, nothing new added
    map_children_milestones_data(
        "unuseddata.csv", import_session, overwritten_csv=fake_data_csv()
    )
    assert len(children) == 6

    # now try with one new genuinely additional child on top of re-importing previous ones

    # now one on it's own
    raise
