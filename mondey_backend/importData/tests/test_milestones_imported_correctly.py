import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os

from insert_milestones_into_database import process_milestones_csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel import select

from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupText

# Use a path relative to the importData directory
csv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "milestones_metadata_(variables).csv",
)


def test_import_works():
    process_milestones_csv(csv_path)

    # Create a session to query the database

    db_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///./db/mondey.db",  # not the same as the normal DB
        # Make sure to refresh and connect to it, it will otherwise appear to be blank!
    )  # will already have all the tables.
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        # Assert that a milestone with data_import_key of DE01_02 exists
        milestone_de01_02 = session.exec(
            select(Milestone).where(Milestone.data_import_key == "DE01_02")
        ).first()
        assert milestone_de01_02 is not None, (
            "Milestone with data_import_key DE01_02 should exist"
        )

        # Assert that the milestone's group text contains "Sehen und"
        milestone_group = session.exec(
            select(MilestoneGroup).where(
                MilestoneGroup.id == milestone_de01_02.group_id
            )
        ).first()
        assert milestone_group is not None

        group_text_de = session.exec(
            select(MilestoneGroupText).where(
                (MilestoneGroupText.group_id == milestone_group.id)
                & (MilestoneGroupText.lang_id == "de")
            )
        ).first()
        assert group_text_de is not None
        assert "Sehen und" in group_text_de.title, (
            f"Group title should contain 'Sehen und', but was '{group_text_de.title}'"
        )

        # Assert that there is no milestone with data_import_key of DA03
        milestone_da03 = session.exec(
            select(Milestone).where(Milestone.data_import_key == "DA03")
        ).first()
        assert milestone_da03 is None, (
            "Milestone with data_import_key DA03 should not exist"
        )

        # Assert that there is no milestone with data_import_key of "CASE"
        milestone_case = session.exec(
            select(Milestone).where(Milestone.data_import_key == "CASE")
        ).first()
        assert milestone_case is None, (
            "Milestone with data_import_key CASE should not exist"
        )

        # Assert that there is no milestone with data_import_key of "TIME057"
        milestone_time057 = session.exec(
            select(Milestone).where(Milestone.data_import_key == "TIME057")
        ).first()
        assert milestone_time057 is None, (
            "Milestone with data_import_key TIME057 should not exist"
        )

        # Assert that there are 208 milestones total in the database
        milestone_count = session.exec(select(Milestone)).all()
        assert len(milestone_count) == 208, (
            f"Expected 208 milestones, but found {len(milestone_count)}"
        )
