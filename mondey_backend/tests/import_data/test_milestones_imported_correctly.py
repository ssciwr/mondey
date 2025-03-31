import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config import milestone_data_csv_path
from sqlmodel import select

# todo: Delete if now not needed with config.py
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mondey_backend.import_data.import_milestones_metadata import (
    import_milestones_metadata,
)
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupText

"""
The database is the same for each test.

The motivation for not having a new import test DB for each test is that some parts (e.g. assigning the childrens
data to milestones) require look up of milestone IDs. Rather than mock the milestones (which means mocking the
entire import data), the tests running sequentially like they would be processed tests

The argument clear_tables allows us to run freshly. That way there is a test_full_import which tests
everything arrives as we expect and provides a way for us to generate and leave the real data ready for
SQL export in the test database.
"""


@pytest.mark.skip(reason="Requires private CSV data not in this repo")
def test_import_works():
    import_session, import_engine = get_import_test_session(create_tables=True)
    import_milestones_metadata(
        import_session, milestone_data_csv_path, clear_existing_milestones=True
    )
    # Assert that a milestone with name of DE01_02 exists
    milestone_de01_02 = import_session.exec(
        select(Milestone).where(Milestone.name == "DE01_02")
    ).first()
    assert milestone_de01_02 is not None, "Milestone with name DE01_02 should exist"

    # Assert that the milestone's group text contains "Sehen und"
    milestone_group = import_session.exec(
        select(MilestoneGroup).where(MilestoneGroup.id == milestone_de01_02.group_id)
    ).first()
    assert milestone_group is not None

    group_text_de = import_session.exec(
        select(MilestoneGroupText).where(
            (MilestoneGroupText.group_id == milestone_group.id)
            & (MilestoneGroupText.lang_id == "de")
        )
    ).first()
    assert group_text_de is not None
    assert "Denken" in group_text_de.title, (
        f"Group title should contain 'Denken', but was '{group_text_de.title}'"
    )

    # Assert that there is no milestone with name of DA03
    milestone_da03 = import_session.exec(
        select(Milestone).where(Milestone.name == "DA03")
    ).first()
    assert milestone_da03 is None, "Milestone with name DA03 should not exist"

    # Assert that there is no milestone with name of "CASE"
    milestone_case = import_session.exec(
        select(Milestone).where(Milestone.name == "CASE")
    ).first()
    assert milestone_case is None, "Milestone with name CASE should not exist"

    # Assert that there is no milestone with name of "TIME057"
    milestone_time057 = import_session.exec(
        select(Milestone).where(Milestone.name == "TIME057")
    ).first()
    assert milestone_time057 is None, "Milestone with name TIME057 should not exist"

    # Assert that there are 208 milestones total in the database
    milestone_count = import_session.exec(select(Milestone)).all()
    assert len(milestone_count) == 208, (
        f"Expected 208 milestones, but found {len(milestone_count)}"
    )
