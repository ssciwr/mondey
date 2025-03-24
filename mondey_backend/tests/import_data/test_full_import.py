"""
The database is the same for each test.

The motivation for not having a new import test DB for each test is that some parts (e.g. assigning the childrens
data to milestones) require look up of milestone IDs. Rather than mock the milestones (which means mocking the
entire import data), the tests running sequentially like they would be processed tests

The argument clear_tables allows us to run freshly. That way there is a test_full_import which tests
everything arrives as we expect and provides a way for us to generate and leave the real data ready for
SQL export in the test database.

This pattern allows us to access the same database (session) in the real code and in tests without duplication,
but without adding a dependency injection library or managing the test data with substantial mocking (because FastAPI
dependency injection can't really work in the context of these imports unless we marked them (wrongly) as routes etc)
"""

"""
from mondey_backend.import_data.import_milestones_metadata import (
    import_milestones_metadata,
)


def test_full_import():
    # This first call clears any existing data in the test database (through import_session), then runs imports
    import_milestones_metadata(
        import_session, path_to_milestones_csv, clear_existing_milestones=True
    )
    # imports basic data, e.g. child DoB, plus milestones for each child
    import_children_with_assigned_milestone_data(import_session, path_to_data_csv)
    # imports the questions about each child, e.g. about their parents. Requires data mapping
    import_childrens_answers_to_questions(import_session, path_to_data_csv)

    # Now we assert a variety of data is present that the import would have generated
    # assert milestone meta data exists
    # assert child exists with right DOB
    # assert childs fragen ueber kind exists
    # assert childs fragen ueber kind answer is correct for the question (mapped correctly into text value)
    # todo: possibly - assert feedback is what we expect for children

"""
