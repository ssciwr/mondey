import pandas as pd

from mondey_backend.databases.mondey import create_mondey_db_and_tables
from mondey_backend.import_data.utils import clear_all_data
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupText
from mondey_backend.models.milestones import MilestoneText

""" Imported so that all tables get created correctly, so that we don't get FK non-exists errors... """

#


def extract_milestone_prefix(text):
    """Extract the prefix from a milestone title."""
    if ":" in text:
        return text.split(":", 1)[0].strip()
    return None


def clean_milestone_title(text):
    """Remove prefix and clean the milestone title."""
    if ":" in text:
        return text.split(":", 1)[1].strip()
    return text.strip()


def is_milestone(row):
    var = row["VAR"]
    label = row["LABEL"]
    dType = row.get("TYPE", "")
    input = row.get("INPUT", "")
    if not (isinstance(var, str) and "_" in var):
        return False
    if dType != "ORDINAL":
        return False
    if input != "SCALE":
        return False
    if not label:
        return False
    return len(label) > 10


def import_milestones_metadata(session, csv_path, clear_existing_milestones=False):
    """Process the milestones CSV file and insert data into the database."""
    df = pd.read_csv(csv_path, sep="\t", encoding="utf-16")
    # If we couldn't read the file with any encoding, raise an error
    if df is None:
        raise ValueError(
            f"Could not read the file {csv_path} with any of the attempted encodings."
        )

    if clear_existing_milestones:
        clear_all_data()
        # Rather than alter the Session fixture/dependency, I did this to be absolutely sure
    # the count of milestones is 0 at the time we begin the test.

    # Filter for milestone rows (those with IDs containing '_')
    milestone_df = df[df["VAR"].str.contains("_")]

    # Ensure the German language exists
    if not session.get(Language, "de"):
        session.add(Language(id="de"))
        session.commit()

    # Group milestones by their prefixes
    milestone_groups = {}
    affix_groups = {}

    # First, identify affixes from the QUESTION column
    for _, row in milestone_df.iterrows():
        var = row["VAR"]
        label = row["LABEL"]
        question = row.get("QUESTION", "")

        # Skip non-milestone rows
        if not is_milestone(row):
            print("Skipping" + label)
            continue
        else:
            print("Keeping " + label)

        # Check if this is an affix group
        if (
            isinstance(question, str)
            and question.startswith("__")
            and question.endswith("__")
        ):
            affix = question.removeprefix("__").removesuffix("__")
            if affix not in affix_groups:
                affix_groups[affix] = []
            affix_groups[affix].append(var)

    # Now process all milestones and assign them to groups
    for _, row in milestone_df.iterrows():
        var = row["VAR"]
        label = row["LABEL"]

        # Skip non-milestone rows
        if not is_milestone(row):
            continue

        # Get the prefix from the label
        prefix = extract_milestone_prefix(label)

        # Check if it belongs to an affix group
        for affix, vars_list in affix_groups.items():
            if var in vars_list:
                prefix = affix if not prefix else affix + " " + prefix
                # e.g. "__Denken__ Sehene und Hoeren
                break

        if prefix:
            if prefix not in milestone_groups:
                milestone_groups[prefix] = []
            milestone_groups[prefix].append((var, label))

    # Create milestone groups and milestones
    group_id_map = {}  # To store group_id for each prefix

    for order, (prefix, milestones) in enumerate(milestone_groups.items(), start=1):
        # Create milestone group
        milestone_group = MilestoneGroup(order=order)
        session.add(milestone_group)
        session.flush()  # To get the ID

        # Create milestone group text
        milestone_group_text = MilestoneGroupText(
            group_id=milestone_group.id, lang_id="de", title=prefix, desc=""
        )
        session.add(milestone_group_text)

        group_id_map[prefix] = milestone_group.id

        # Create milestones for this group
        for milestone_order, (var, label) in enumerate(milestones, start=1):
            clean_title = clean_milestone_title(label)

            print("Setting data import key to:", var)

            milestone = Milestone(
                group_id=milestone_group.id,
                order=milestone_order,
                data_import_key=var,
                expected_age_months=12,  # Default value, since they don't have expected ages in the csv?
            )
            session.add(milestone)
            session.flush()  # To get the ID

            # Create milestone text
            milestone_text = MilestoneText(
                milestone_id=milestone.id,
                lang_id="de",
                title=clean_title,
                desc="",
                obs="",
                help="",
            )
            session.add(milestone_text)

    session.commit()
    print(
        f"Successfully imported {sum(len(m) for m in milestone_groups.values())} milestones in {len(milestone_groups)} groups"
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python import_milestones_metadata.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    import_session, import_engine = get_import_test_session()
    create_mondey_db_and_tables(optional_engine=import_engine)
    # asyncio.run(create_user_db_and_tables()) We don't need this for milestones/children, I believe.

    import_milestones_metadata(import_session, csv_path)
