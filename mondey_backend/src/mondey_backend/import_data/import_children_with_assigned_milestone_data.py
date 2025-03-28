import asyncio
import csv
import pathlib

from sqlmodel import select
from tqdm import tqdm

from mondey_backend.import_data.utils import generate_parents_for_children
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession


def map_children_milestones_data(path, session, overwritten_csv=False):
    """
    Based on the data file, this creates the Children and respective User Parents(1 for each child). It fills out
    the required basic (hardcoded) information for each child, like date of birth. It also saves all the milestone
    data using milestone answering sessions/milestone answers, because this information uses a consistent value
    encoding (so we don't need to do a coding mapping, see `import_childrens_question_answers_data` for more info.

    This script requires the milestones meta data has been loaded via import_milestones_metadata, and after running,
    all the children and Meta data will be present! Thus, after this script, we can already look at the milestones data
    or for example generate a histogram to look at the distribution of milestone data throughout ages of children.

    This script fills out the milestone data.

    :param path: path to the data. Ignored if overwritten_csv is not False.
    :param session: The *import* session database for the mondey database.
    :param overwritten_csv: an in memory CSV for testing correct parsing
    """
    csv_path = pathlib.Path(path)
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
    with (
        overwritten_csv if overwritten_csv else open(csv_path, encoding="utf-16")
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")

        # Make parents in a batch query.
        child_ids = [row["CASE"] for row in reader]
        parent_id_map = asyncio.run(generate_parents_for_children(child_ids))

        # Process each row (child)
        for row in tqdm(reader):
            child_id = int(row["CASE"])
            if str(row["FK01"]) == "-9" or str(row["FK02"]) == "-9":
                print(
                    "Skipping child has who is missing essential birth month/year data."
                )
                continue
            # Check if child already exists
            existing_child = session.execute(
                select(Child).where(Child.id == child_id)
            ).scalar_one_or_none()

            print(row["FK01"])
            print("And month:")
            print(row["FK02"])

            # Hardcoded
            birth_year_mapping = {
                9: 2025,
                1: 2024,
                2: 2023,
                3: 2022,
                4: 2021,
                5: 2020,
                6: 2019,
                7: 2018,
                8: 2017,  # Converting "Vor 2018" to 2017
            }

            birth_month_mapping = {
                1: 1,  # Januar
                2: 2,  # Februar
                3: 3,  # März
                4: 4,  # April
                5: 5,  # Mai
                6: 6,  # Juni
                7: 7,  # Juli
                8: 8,  # August
                9: 9,  # September
                10: 10,  # Oktober
                11: 11,  # November
                12: 12,  # Dezember
            }

            if not existing_child:
                # Make the parent first, for parent questions and milestone answering sessions.
                parents_id = parent_id_map[
                    child_id
                ]  # still works: get_childs_parent_id(child_id)

                # Create a new child
                child = Child(
                    id=child_id,
                    name=f"Imported Child {child_id}",
                    birth_year=birth_year_mapping[int(row["FK01"])],  # FK01, mapped...
                    birth_month=birth_month_mapping[int(row["FK02"])],
                    user_id=parents_id,
                    has_image=False,
                )
                session.add(child)
                session.commit()
                print(f"Created child with ID: {child_id}")
            else:
                # @liam this supports updating with future milestone answer sessions for the same children, but,
                # we probably want to know from the researchers whether to overwrite or add new milestones, especially
                # what to do when the milestone level is the same as existing data (i.e. probably duplicate mistake)
                # So for now it will raise a ValueError to prevent messing up the data on import, to be safe.
                child = existing_child
                print(f"Using existing child with ID: {child_id}")
                raise ValueError(
                    "There appears to be duplicate data for a child - they already have data. "
                    "Are you sure you want to add further milestone data, possibly duplicating answers?"
                )

            # Create a milestone answer session for this child
            answer_session = MilestoneAnswerSession(
                child_id=child_id,
                user_id=parents_id,
                expired=False,
                included_in_statistics=True,
            )
            session.add(answer_session)
            session.commit()

            # Process each milestone column
            for column, milestone_id in milestone_mapping.items():
                if column in row:
                    answer_value = row[column]

                    # Skip if the answer is -9 (not answered)
                    if answer_value == "-9" or answer_value == "":
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
                    except (ValueError, TypeError) as err:
                        raise ValueError(
                            "Unable to save a milestone, this indicates a major issue."
                        ) from err

            # Commit all answers for this child
            session.commit()


if __name__ == "__main__":
    import_session, import_engine = get_import_test_session()
    map_children_milestones_data("data.csv", import_session)
