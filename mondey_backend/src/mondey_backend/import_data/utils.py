from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session
from sqlmodel import select

from mondey_backend.databases.mondey import create_mondey_db_and_tables_themselves
from mondey_backend.models.children import Child
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText
from mondey_backend.models.users import User
from mondey_backend.models.users import UserCreate

script_dir = Path(__file__).parent.parent.parent.parent.absolute()
database_file_path = script_dir / "src/mondey_backend/import_data/db/mondey.db"

# This is the *test* database in import_data directory. Not the normal database, to avoid overwrites/issues
db_url = "sqlite:////" + str(database_file_path)  # not the same as the normal DB
# Make sure to refresh and connect to it, it will otherwise appear to be blank!
engine = create_engine(db_url)

current_database_file_path = (
    script_dir / "src/mondey_backend/import_data/current_db/current_mondey.db"
)

current_db_url = "sqlite:////" + str(current_database_file_path)
current_engine = create_engine(current_db_url)

# users_database_file_path = script_dir / "src/mondey_backend/import_data/db/users.db"
users_database_file_path = (
    script_dir / "src/mondey_backend/import_data/current_db/current_users.db"
)

print("Users database file path", users_database_file_path)

async_users_engine = create_async_engine(
    f"sqlite+aiosqlite:///{users_database_file_path}"
)

async_import_session_maker = async_sessionmaker(
    async_users_engine, expire_on_commit=False
)

# All 3 files come from SoSci Spreadsheet export...
labels_path = "labels_encoded.csv"  # originally codebook_MONDEY_0-6_2025-03-20_16-16.xlsx (export it to CSV first)
data_path = "data.csv"  # originally data_MONDEY_0-6_2025-03-20_16-16.csv
milestones_metadata_path = "milestones_metadata_(variables).csv"  # originally variables_MONDEY_0-6_2025-03-20_16-16.csv
# The other "Values" CSV SoSci file is not used in this process.

# From the researchers later: classifying questions as required / isToParent.
questions_configured_path = "questions_specified.csv"  # so this is questions.csv generated by `generate_list_of_questions.py" once filled out  # (with isToParent)


def get_childs_parent_id(session: Session, child_id: int) -> int:
    """
    Get the user_id (parent ID) of a Child object

    Args:
        session: Database session
        child_id: ID of the child

    Returns:
        The user_id of the child's parent
    """
    child = session.execute(
        select(Child).where(Child.id == child_id)
    ).scalar_one_or_none()
    if not child:
        raise ValueError(f"Child with ID {child_id} not found")
    return child.user_id


async def clear_users_database():
    """Clear all data from the users database (async_users_session)."""
    print("Clearing users database...")

    async with async_users_engine.begin() as session:
        user_count = await session.execute(text('SELECT COUNT(*) FROM "user"'))
        user_count = user_count.scalar()

        count_users = await session.execute(
            text("SELECT COUNT(*) FROM \"user\" WHERE email LIKE '%parent_of_%'")
        )
        total_users = count_users.scalar()
        has_test_user = total_users in [
            321,
            642,
        ]  # was going to do % 321 == 0, but that includes when 0 are found!

        print("Total users:", total_users)
        if total_users == 0:
            print(f"Nothing to do - {count_users} no test users exist, so none deleted")
            return False
        if not has_test_user or user_count < 250:  # probably real users
            raise Exception(
                f"Safety check failed! Found {user_count} users and no test users with example.com emails. "
                "This could be real data - operation aborted."
            )

        # Get sample of emails for debugging
        result = await session.execute(
            text(
                "SELECT id, email FROM \"user\" WHERE email LIKE '%artificialimporteddata.csv%' LIMIT 3"
            )
        )
        sample_users = result.fetchall()
        print("Sample users that should be deleted:")
        for user_id, email in sample_users:
            print(f"  ID: {user_id}, Email: {email}")

        # Try more direct approach with explicit transaction
        try:
            # Delete the users
            result = await session.execute(
                text("DELETE FROM \"user\" WHERE email LIKE '%parent_of_%'")
            )
            rows_deleted = result.rowcount
            print(f"DELETE statement affected {rows_deleted} rows")

            # Explicitly commit the transaction

            # Verify deletion
            result = await session.execute(
                text(
                    "SELECT COUNT(*) FROM \"user\" WHERE email LIKE '%artificialimporteddata.csv%'"
                )
            )
            remaining = result.scalar()
            print(f"Remaining matching users after deletion: {remaining}")
            print("Successfully cleared all data from users database")
            if (
                input(
                    f"Users deleted, leaving {remaining} users. Type 'undo' to cancel and undo this, or anything else to proceed"
                )
                == "undo"
            ):
                await session.rollback()
                print("Rolled back changes.")
                raise Exception("Finished script due to undo")
            else:
                await session.commit()
                print("Transaction committed successfully")
        except Exception as err:
            print("Error encountered. Rolling back")
            print(err)
            await session.rollback()


# Deprecated, as script now expects directory with existing data (in terms of Milestones/Milestonegroups,
# but not children/users/question-answers).
def clear_all_data(session):
    """Clear all data but do not delete the databases."""

    # Safety check: Verify this is test data
    child_count = session.execute(text("SELECT COUNT(*) FROM child")).scalar()
    has_test_child = (
        session.execute(
            text("SELECT COUNT(*) FROM child WHERE name = 'Imported Child 159'")
        ).scalar()
        > 0
    )

    # Abort if safety checks fail
    if (child_count != 321 and not has_test_child) and child_count != 0:
        raise Exception(
            "Safety check failed! Expected 321 rows in child table and at least one "
            "child with name 'Imported Child 159'. This could be real data - operation aborted."
        )

    metadata = MetaData()
    metadata.reflect(bind=engine)

    session.execute(text("PRAGMA foreign_keys = OFF"))
    for table in metadata.sorted_tables:
        session.execute(text(f"DELETE FROM {table.name}"))
    session.execute(text("PRAGMA foreign_keys = ON"))
    session.commit()

    asyncio.run(clear_users_database())


def get_import_test_session(create_tables=False):
    with Session(engine) as session:
        if create_tables:  # Largely for use in the tests.
            create_mondey_db_and_tables_themselves(engine)
        return session, engine


# This will ALREADY have the current milestones.
def get_import_current_session():
    with Session(current_engine) as current_session:
        return current_session, current_engine


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
                    lang_id="de",  # German
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
                    lang_id="de",  # German
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
                    lang_id="de",  # German
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
                    lang_id="de",  # German
                )
            },
        )
        session.add(child_question)
        return child_question


async def create_parent_for_child(
    user_session: AsyncSession, user_db: SQLAlchemyUserDatabase, child_id: int
) -> User:
    """
    Create a parent user for a given child
    """
    # Generate a unique username and email based on child's details
    username = f"parent_of_{child_id}"
    email = f"{username}@artificialImportedData.csv"

    # Create user object
    user_create = UserCreate(
        email=email,
        password="$$$$testUser$$$$432hjdfioj3409lk",
        is_researcher=False,
        full_data_access=False,
        research_group_id=0,
    )

    # Manually create User instance with specific attributes
    user = User(
        email=user_create.email,
        hashed_password="$$$$testUser$$$$432hjdfioj3409lk$$$$hashed$$$$",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        is_researcher=user_create.is_researcher or False,
        full_data_access=user_create.full_data_access or False,
        research_group_id=user_create.research_group_id or 0,
    )

    # Add the user to the session
    user_session.add(user)
    await user_session.flush()

    print("Created the user parent!!")

    return user


async def generate_parents_for_children(child_ids: list[int]) -> dict[int, int]:
    """
    Generate parents in bulk for given child IDs

    Returns:
        A dictionary mapping child IDs to parent IDs
    """
    child_parent_map = {}

    async with async_import_session_maker() as user_import_session:
        user_db: SQLAlchemyUserDatabase = SQLAlchemyUserDatabase(
            user_import_session, User
        )
        try:
            for child_id in child_ids:
                parent = await create_parent_for_child(
                    user_import_session, user_db, child_id
                )
                print("created parent", parent)
                child_parent_map[child_id] = parent.id

            await user_import_session.commit()

            return child_parent_map

        except Exception as e:
            print(f"Error generating parents: {e}")
            raise


def update_or_create_user_answer(
    session: Session,
    user_or_child_id: int,
    question_id: int,
    answer_text: str,
    set_only_additional_answer: bool = False,
    is_child_question=True,
):
    """
    Upsert the answers to questions, by ID, handling different kinds of answers.
    """
    # Use with_for_update to lock the row during the transaction
    query = (
        (
            select(ChildAnswer)
            .where(ChildAnswer.child_id == user_or_child_id)
            .where(ChildAnswer.question_id == question_id)
            .with_for_update(skip_locked=True)
        )
        if is_child_question
        else (
            select(UserAnswer)
            .where(UserAnswer.user_id == user_or_child_id)
            .where(UserAnswer.question_id == question_id)
            .with_for_update(skip_locked=True)
        )
    )

    print(
        "Adding or updating question!",
        "QID: ",
        str(question_id),
        "UID",
        str(user_or_child_id),
    )

    existing_answer = session.execute(query).scalar_one_or_none()

    # If answer exists, update it
    if existing_answer and answer_text is not None and answer_text != "":
        print("Existing answer...")
        try:
            if set_only_additional_answer:
                print("Setting additional answer")
                # Only update additional_answer if flag is set. Leave any set "answer", e.g. "Other", previously set...
                existing_answer.additional_answer = answer_text
            else:
                # Update solely answer property, the default (especially for "select" options).
                existing_answer.answer = answer_text

            print("Adding to SQL sesion...")
            session.add(existing_answer)
            return True, existing_answer

        except Exception as e:
            # Log the error, rollback the session
            print(f"Error updating existing answer: {e}")
            session.rollback()
    else:
        if set_only_additional_answer:
            print(
                "Additional answer with no found base question. This could be a question which is independent, "
                "but happens to have [01] and 'Andere' in the name, like 'Andere Diagnosen', which is okay, "
                "but it could indicate data processing has gone wrong."
            )
        # If no existing answer
        try:
            print(
                "Not existing answer, so making a new one..",
                "Answer:",
                str(answer_text),
            )
            new_answer = (
                ChildAnswer(
                    child_id=user_or_child_id,
                    question_id=question_id,
                    answer=answer_text,
                )
                if is_child_question
                else UserAnswer(
                    user_id=user_or_child_id,
                    question_id=question_id,
                    answer=answer_text,
                )
            )
            session.add(new_answer)
            return False, new_answer

        except Exception as e:
            # Handle potential integrity errors
            print(f"Error creating new answer: {e}")
            session.rollback()
            raise


def get_question_filled_in_to_parent(questions_done_df, variable, debug_print=False):
    csv_match = questions_done_df[questions_done_df["variable"] == variable]

    match_found = not csv_match.empty and str(csv_match.iloc[0]["isToParent"]) in [
        "true",
        "ja",
        "yes",
    ]
    if debug_print:
        print("So match found was: ", "True" if match_found else "False")
    return match_found


def get_question_filled_in_required(questions_done_df, variable):
    return False  # They will adjust this in the UI later.
