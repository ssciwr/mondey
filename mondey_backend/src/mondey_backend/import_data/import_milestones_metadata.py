import pandas as pd
from sqlalchemy import select

from mondey_backend.databases.mondey import create_mondey_db_and_tables
from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneText

""" Imported so that all tables get created correctly, so that we don't get FK non-exists errors... """


def find_milestone_based_on_label(session, label):
    if ":" in label:
        label = label.split(":", 1)[1].lstrip()

    print("Milestone search - using preprocessed label for desc search as: ", label)

    stmt = select(MilestoneText).where(MilestoneText.desc == label)
    milestone_text = session.scalars(stmt).first()

    if not milestone_text:
        stmt = select(MilestoneText).where(MilestoneText.desc == label.rstrip("."))
        milestone_text = session.scalars(stmt).first()

    # Some german translations on the website are (missing intentionally?) the starting "Das".
    if not milestone_text:
        dasified_label = label.removeprefix("Das ")
        if dasified_label == "Kind erkennt, ob sich zwei Worte reimen oder nicht.":
            dasified_label = "Kind erkennt, ob sich zwei Worte reimen oder nicht. "
        if (
            dasified_label
            == "Kind erkennt, wenn Wörter mit dem gleichen Buchstaben beginnen (z.B. Haus/Hose, Brot/Besen, Ampel/Apfel)."
        ):
            dasified_label = "Kind erkennt, wenn Wörter mit dem gleichen Buchstaben beginnen (z.B. Haus/Hose, Brot/Besen, Ampel/Apfel."

        print("Trying with Dasified label: ", dasified_label)
        stmt = select(MilestoneText).where(MilestoneText.desc == dasified_label)
        milestone_text = session.scalars(stmt).first()

    if milestone_text:
        return milestone_text.milestone_id
    return None


def update_milestone_with_name_property(session, milestone_id, var):
    # Get the milestone object using select
    stmt = select(Milestone).where(Milestone.id == milestone_id)
    milestone = session.scalars(stmt).first()

    if milestone:
        # Update the name property
        milestone.name = var
        session.commit()
        return True
    return False


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


def derive_milestone_group_from_milestone_string_id(string_id: str) -> str | None:
    """
    GM = Grobmotorik
    HM = Handmotorik
    SE = Soziale Entwicklung
    SP = Sprache
    SV = Schulische Vorläuferfertigkeiten
    UZ = Umgang mit inneren Zuständen
    DE = Denken

    valid_milestone_groups_actual_names = {
        "GM": "Grobmotorik",
        "HM": "Handmotorik",
        "SE": "Soziale Entwicklung",
        "SP": "Sprache",
        "SV": "Schulische Vorläuferfertigkeiten",
        "UZ": "Umgang mit inneren Zuständen",
        "DE": "Denken",
    }
    """
    valid_milestone_groups = {
        "GM": "2",
        "HM": "1",
        "SE": "5",
        "SP": "4",
        "SV": "7",
        "UZ": "6",
        "DE": "3",
    }
    if len(string_id) > 2 and string_id[0:2] in valid_milestone_groups:
        return valid_milestone_groups[string_id[0:2]]
    return None


def import_milestones_metadata(real_session, csv_path):
    """Process the milestones CSV file and insert data into the database."""
    df = pd.read_csv(csv_path, sep="\t", encoding="utf-16")

    # Filter for milestone rows (those with IDs containing '_')
    milestone_df = df[df["VAR"].str.contains("_")]

    # Ensure the German language exists
    # it definitely should for real sessions, but due to UTF-8/UTF-16 encoding issues (with the original
    # 3 CSVs and later one), we double check the SQL lang is set to support german.
    if not real_session.get(Language, "de"):
        real_session.add(Language(id="de"))
        real_session.commit()

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

        derived_milestone_group = derive_milestone_group_from_milestone_string_id(var)

        # Get the prefix from the label
        prefix = extract_milestone_prefix(label)

        # Check if it belongs to an affix group
        for affix, vars_list in affix_groups.items():
            if var in vars_list:
                prefix = affix if not prefix else affix + " " + prefix
                # e.g. "__Denken__ Sehene und Hoeren
                break

        if derived_milestone_group:
            if derived_milestone_group not in milestone_groups:
                milestone_groups[derived_milestone_group] = []
            milestone_groups[derived_milestone_group].append((var, label))
        elif prefix:
            if prefix not in milestone_groups:
                milestone_groups[prefix] = []
            milestone_groups[prefix].append((var, label))

    # Create milestone groups and milestones
    # deprecated: group_id_map = {}  # To store group_id for each prefix

    for _order, (_prefix, milestones) in enumerate(milestone_groups.items(), start=1):
        """
        Deprecated: When we created, rather than merged, milestone groups.
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
        """
        # Create milestones for this group
        for _milestone_order, (var, label) in enumerate(milestones, start=1):
            """
            Deprecated: When we used to create milestones, rather than merge with existing.
            clean_title = clean_milestone_title(label)

            print("Setting data import key to:", var)

            milestone = Milestone(
                group_id=prefix,
                order=milestone_order,
                name=var,
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
            """
            milestone_id = find_milestone_based_on_label(real_session, label)
            # label: remove anything before ":" char, then look up
            # milestonetext which has a "title" property equal to the label after the ':' var (+ removePrefix(" ").
            # milestonetext has an milestone_id field, use this to get the milestone ID.
            # by doing this the whole script works like before

            update_milestone_with_name_property(real_session, milestone_id, var)
            # now update the milestone with milestone_id as passed with the "name" property being set/updated to "var".
            print(
                "Milestone should have been updated!", milestone_id, label, "var:", var
            )

            if not milestone_id:
                print("Unaccounted fo milestone!")
                raise ValueError("Missing milestone - reconsider importing.")
    real_session.commit()
    print(
        f"Successfully imported {sum(len(m) for m in milestone_groups.values())} milestones in {len(milestone_groups)} groups"
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: python import_milestones_metadata.py <path_to_milestones_csv> <?clear_existing_milestones bool>, e.g."
            "python import_milestones_metadata.py milestones_metadata_(variables).csv"
        )
        sys.exit(1)

    csv_path = sys.argv[1]
    clear_existing_milestones = False
    if len(sys.argv) > 2:
        clear_existing_milestones = sys.argv[2] == "true"

    if clear_existing_milestones and (
        input(
            "This will wipe your DB data! Are you certain you want to *delete all data*? (y/n)"
        )
        != "y"
    ):
        exit()

    import_session, import_engine = get_import_test_session()
    real_session, real_engine = get_import_current_session()
    create_mondey_db_and_tables(optional_engine=import_engine)

    import_milestones_metadata(real_session, csv_path)
