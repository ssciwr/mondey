import codecs
import os
import tempfile

from sqlmodel import select

from mondey_backend.import_data.import_children_with_assigned_milestone_data import (
    map_children_milestones_data,
)
from mondey_backend.models.children import Child


def create_test_csv_file(filename, child_ids=None):
    """
    Create a UTF-16 encoded CSV file with test data for specified child IDs.

    Args:
        filename: Name of the CSV file to create
        child_ids: List of child IDs to include in the CSV. If None, defaults to [159, 208]

    Returns:
        Path to the created CSV file
    """
    if child_ids is None:
        child_ids = [159, 208]

    headers = [
        "CASE",
        "FK01",
        "FK02",
    ]

    # Create the content as tab-separated data
    content = "\t".join(headers) + "\n"

    # Add each row
    for child_id in child_ids:
        row = [str(child_id), "1", "9"]
        content += "\t".join(row) + "\n"

    # Write the content to a UTF-16 encoded file with BOM
    with codecs.open(filename, "w", encoding="utf-16") as f:
        f.write(content)

    return filename

    return filename


def test_duplicates_are_ignored_during_import(session):
    """Test that duplicate children are ignored when importing data"""
    print("Importing.")
    import_session = session  # use per-test reset DB for this purpose.

    # Create temporary directory for test CSV files
    temp_dir = tempfile.mkdtemp()

    # First import with the default children (159, 208)
    csv_file1 = os.path.join(temp_dir, "children_import_test1.csv")
    create_test_csv_file(csv_file1)
    map_children_milestones_data(csv_file1, import_session)

    # Verify first child's data
    child_id = 159
    child_name = f"Imported Child {child_id}"
    child = import_session.execute(
        select(Child).where(Child.name == child_name)
    ).scalar_one_or_none()

    assert child.birth_year == 2024
    assert child.birth_month == 9

    # Check all children were imported
    children = import_session.exec(select(Child)).all()
    assert len(children) == 6  # Initial 4 + our 2 new ones

    # Test reimporting the same data doesn't create duplicates
    csv_file2 = os.path.join(temp_dir, "children_import_test2.csv")
    create_test_csv_file(csv_file2)
    map_children_milestones_data(csv_file2, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 6  # Should still be 6

    # Test adding one new child while reimporting the existing ones
    csv_file3 = os.path.join(temp_dir, "children_import_test3.csv")
    create_test_csv_file(csv_file3, child_ids=[159, 208, 300])
    map_children_milestones_data(csv_file3, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 7  # Should now be 7 (6 previous + 1 new)

    # Test importing just one new child on its own
    csv_file4 = os.path.join(temp_dir, "children_import_test4.csv")
    create_test_csv_file(csv_file4, child_ids=[301])
    map_children_milestones_data(csv_file4, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 8  # Should now be 8

    # Test importing multiple new children
    csv_file5 = os.path.join(temp_dir, "children_import_test5.csv")
    create_test_csv_file(csv_file5, child_ids=[302, "400", "401_SomeChars"])
    map_children_milestones_data(csv_file5, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 11  # Should now be 11

    # test string based child IDs also don't get duplicated.
    csv_file6 = os.path.join(temp_dir, "children_import_test6.csv")
    create_test_csv_file(csv_file6, child_ids=["401_SomeChars"])
    map_children_milestones_data(csv_file6, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 11  # Should now be 11

    # yet another new one with another duplicate.
    csv_file6 = os.path.join(temp_dir, "children_import_test7.csv")
    create_test_csv_file(csv_file6, child_ids=["401_SomeChars", "40634_SomeChars"])
    map_children_milestones_data(csv_file6, import_session)

    children = import_session.exec(select(Child)).all()
    assert len(children) == 12
