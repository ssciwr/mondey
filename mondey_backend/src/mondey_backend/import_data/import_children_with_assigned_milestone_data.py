import csv
import os
import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel import select
from tqdm import tqdm

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession


def map_children_milestones_data():
    # Open the CSV file with UTF-16 encoding
    csv_path = pathlib.Path("data.csv")

    db_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///./db/mondey.db",  # not the same as the normal DB
        # Make sure to refresh and connect to it, it will otherwise appear to be blank!
    )  # will already have all the tables.
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        milestone_query = select(Milestone)
        milestones = session.execute(milestone_query).scalars().all()

        # Create a mapping from coded_key (column name) to milestone_id
        milestone_mapping = {}
        milestone_group_mapping = {}

        for milestone in milestones:
            if milestone.data_import_key:
                milestone_mapping[milestone.data_import_key] = milestone.id
                milestone_group_mapping[milestone.id] = milestone.group_id

        # Print the mapping for verification
        print("Milestone mapping (column name -> milestone ID):")
        for key, value in milestone_mapping.items():
            print(f"  {key} -> {value}")

        # Now process the CSV file
        with open(csv_path, encoding="utf-16") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t")

            # Process each row (child)
            for row in tqdm(reader):
                child_id = int(row["CASE"])

                # Check if child already exists
                existing_child = session.execute(
                    select(Child).where(Child.id == child_id)
                ).scalar_one_or_none()

                if not existing_child:
                    # Create a new child
                    child = Child(
                        id=child_id,
                        name=f"Imported Child {child_id}",
                        birth_year=2020,  # Default values since not in CSV
                        birth_month=1,  # Default values since not in CSV
                        user_id=1,  # Default user ID
                        has_image=False,
                    )
                    session.add(child)
                    session.commit()
                    print(f"Created child with ID: {child_id}")
                else:
                    child = existing_child
                    print(f"Using existing child with ID: {child_id}")

                # Create a milestone answer session for this child
                answer_session = MilestoneAnswerSession(
                    child_id=child_id,
                    user_id=1,  # Default user ID
                    expired=False,
                    included_in_statistics=True,
                )
                session.add(answer_session)
                session.commit()
                print(
                    f"Created answer session with ID: {answer_session.id} for child {child_id}"
                )

                # Process each milestone column
                for column, milestone_id in milestone_mapping.items():
                    if column in row:
                        answer_value = row[column]

                        # Skip if the answer is -9 (not answered)
                        if answer_value == "-9":
                            continue

                        # Convert answer to integer and adjust for off-by-one difference
                        try:
                            answer_int = int(answer_value)
                            # Remap the values: 1->0, 2->1, 3->2, 4->3
                            if 1 <= answer_int <= 4:
                                adjusted_answer = answer_int - 1

                                # Create milestone answer
                                milestone_answer = MilestoneAnswer(
                                    answer_session_id=answer_session.id,
                                    milestone_id=milestone_id,
                                    milestone_group_id=milestone_group_mapping.get(
                                        milestone_id
                                    ),
                                    answer=adjusted_answer,
                                )
                                session.add(milestone_answer)
                                print(
                                    f"Added answer for milestone {milestone_id}: {adjusted_answer}"
                                )
                        except (ValueError, TypeError):
                            print(
                                f"Skipping invalid answer value for {column}: {answer_value}"
                            )

                # Commit all answers for this child
                session.commit()
                print(f"Committed all answers for child {child_id}")
                print("-" * 40)


if __name__ == "__main__":
    map_children_milestones_data()
