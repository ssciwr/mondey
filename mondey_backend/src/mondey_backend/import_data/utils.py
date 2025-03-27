from __future__ import annotations

from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlmodel import Session

from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText

script_dir = Path(__file__).parent.parent.parent.parent.absolute()
database_file_path = script_dir / "src/mondey_backend/import_data/db/mondey.db"

# This is the *test* database in import_data directory. Not the normal database, to avoid overwrites/issues
db_url = "sqlite:////" + str(database_file_path)  # not the same as the normal DB
# Make sure to refresh and connect to it, it will otherwise appear to be blank!
engine = create_engine(db_url)

# All 3 come from SoSci...
labels_path = "labels_encoded.csv"  # originally codeback...xlsx
data_path = "data.csv"  # originally
milestones_metadata_path = "milestones_metadata_(variables).csv"  # originally variables
questions_configured_path = (
    "questions_specified.csv"  # so this is questions.csv once filled out
)
# (with isToParent)


def clear_all_data(session):
    """Clear all data but do not delete the databases."""
    metadata = MetaData()
    metadata.reflect(bind=engine)

    session.execute(text("PRAGMA foreign_keys = OFF"))
    for table in metadata.sorted_tables:
        session.execute(text(f"DELETE FROM {table.name}"))
    session.execute(text("PRAGMA foreign_keys = ON"))
    session.commit()


def get_import_test_session():
    with Session(engine) as session:
        return session, engine


""" (For PR review) - Instead of this, I could add a ImportManager with a @contextamanger get_session, but basically,
I think it's useful for tests to just get_import_test_session (we know the strain on the DB won't be crazy with this
amount of data)

I can refactor it if useful, as I am not too happy just having functions exported from several files that are all
doing the same thing (importing), but at the same time I think it is pretty clear how they function for a one-off
import process. I think the individual tests for data existing, plus the full import to test each function can work
sequentially, should together confirm whether import works well or not.
"""


def save_select_question(
    variable,
    variable_label,
    options_json,
    options_str,
    questions_configured_csv,
    session,
):
    """
    Save a multiple-choice question as either a ChildQuestion or UserQuestion

    :param variable: Variable name
    :param variable_label: Question label
    :param options_json: Prepared options JSON
    :param options_str: Prepared options string
    :param labels_df: Optional labels DataFrame for additional context
    :param debug: Debug flag
    """
    debug = False
    is_to_parent = get_question_filled_in_to_parent(questions_configured_csv, variable)
    is_required = get_question_filled_in_required(questions_configured_csv, variable)

    if debug:
        print(f"Processing select question: {variable}")
        print(f"Is to parent: {is_to_parent}")
        print(f"Is required: {is_required}")

    # Determine the appropriate question type
    if is_to_parent:
        # Create UserQuestion for the parent
        user_question = UserQuestion(
            component="select",
            type="text",
            required=is_required,
            text={
                "de": UserQuestionText(
                    question=variable + ": " + variable_label,
                    options_json=options_json,
                    options=options_str,
                    lang_id=1,  # German
                )
            },
        )
        session.add(user_question)
        return user_question
    else:
        # Create ChildQuestion if not a parent question
        child_question = ChildQuestion(
            component="select",
            type="text",
            required=is_required,
            text={
                "de": ChildQuestionText(
                    question=variable + ": " + variable_label,
                    options_json=options_json,
                    options=options_str,
                    lang_id=1,  # German
                )
            },
        )
        session.add(child_question)
        return child_question


def save_text_question(
    variable, variable_label, previous_variable, questions_configured_csv, session
):
    debug = False
    """
    Save a text question as either a ChildQuestion or UserQuestion

    By default as a child question, but as a user question if that has been configured.
    """

    is_to_parent = get_question_filled_in_to_parent(questions_configured_csv, variable)
    is_required = get_question_filled_in_required(questions_configured_csv, variable)

    if debug:
        print(f"Processing text question: {variable}")
        print(f"Is to parent: {is_to_parent}")
        print(f"Is required: {is_required}")

    # Determine the appropriate question type
    if is_to_parent:
        print(variable)
        # Create UserQuestion for the parent
        user_question = UserQuestion(
            component="text",
            type="text",
            required=is_required,
            text={
                "de": UserQuestionText(
                    question=variable + ": " + variable_label,
                    lang_id=1,  # German
                )
            },
        )
        session.add(user_question)
        return user_question
    else:
        # Create ChildQuestion if not a parent question
        child_question = ChildQuestion(
            component="text",
            type="text",
            required=is_required,
            text={
                "de": ChildQuestionText(
                    question=variable + ": " + variable_label,
                    lang_id=1,  # German
                )
            },
        )
        session.add(child_question)
        return child_question


def get_question_filled_in_to_parent(questions_done_df, variable):
    csv_match = questions_done_df[questions_done_df["variable"] == variable]
    return not csv_match.empty and str(csv_match.iloc[0]["isToParent"]) in [
        "true",
        "ja",
        "yes",
    ]


def get_question_filled_in_required(questions_done_df, variable):
    return False  # They will adjust this in the UI later.
