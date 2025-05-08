import pytest
from sqlmodel import select

from mondey_backend.import_data.import_children_with_assigned_milestone_data import (
    map_children_milestones_data,
)
from mondey_backend.import_data.utils import clear_all_data
from mondey_backend.import_data.utils import get_import_test_session
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


@pytest.mark.skip(reason="Needs private local CSV data")
def test_childs_age_is_recorded_accurately():
    import_session, import_engine = get_import_test_session(create_tables=True)
    clear_all_data(import_session)
    await map_children_milestones_data(
        "data.csv", import_session, overwritten_csv=fake_data_csv()
    )
    child_id = 159
    child_name = f"Imported Child {child_id}"
    child = import_session.execute(
        select(Child).where(Child.name == child_name)
    ).scalar_one_or_none()

    assert child.birth_year == 2024
    assert child.birth_month == 9


@pytest.mark.skip(reason="Needs private local CSV data")
def test_childs_age_is_recorded_accurately_alternative():
    import_session, import_engine = get_import_test_session(create_tables=True)
    clear_all_data(import_session)
    await map_children_milestones_data(
        "data.csv", import_session, overwritten_csv=fake_data_csv()
    )
    child_id = 208
    child = import_session.execute(
        select(Child).where(Child.id == child_id)
    ).scalar_one_or_none()
    assert child.birth_year == 2020
    assert child.birth_month == 6
