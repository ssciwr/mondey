from insert_milestones_into_database import process_milestones_csv

csv_path = "milestones_metadata_(variables).csv"


def test_import_works():
    process_milestones_csv(csv_path)
