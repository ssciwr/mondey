import logging
import os
import shutil

import pandas as pd
import pytest
import pytest_asyncio  # Import this for newer versions
from sqlalchemy import func
from sqlmodel import select
from sqlmodel import text

from mondey_backend.import_data.manager.data_manager import ImportPaths
from mondey_backend.import_data.manager.import_manager import ImportManager
from mondey_backend.models.children import Child
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import UserAnswer

# Path constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BASE_CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "src",
    "mondey_backend",
    "import_data",
    "additional_data_full_backup.csv",
)
LABELS_CSV_PATH = os.path.join(
    PROJECT_ROOT, "src", "mondey_backend", "import_data", "labels_encoded.csv"
)
# Test directory
TEST_DIR = os.path.join(os.path.dirname(__file__))  # Current directory
TEST_CSV_PATH = os.path.join(TEST_DIR, "test_data.csv")

logger = logging.getLogger(__name__)


def insert_test_questions(session):
    """Insert test questions into the database"""

    # The below IDs and type reflect our real questions but with AI randomised-replaced text/answer options/IDs
    # Note question 3 for userquestion is excluded because conftest includes it!
    user_questions_sql = """
    INSERT INTO userquestion (id, component, type, options, additional_option, required, name, "order", visibility) VALUES
    (4, 'select', 'text', 'Apple;Banana;Cherry;Grape;Kiwi;Mango;Peach;Pear;Plum;Strawberry', 'Andere', 0, 'fruit_selection_456', 1, 1),
    (5, 'select', 'text', 'Monday;Tuesday;Wednesday;Thursday;Friday;Saturday;Sunday', '', 0, 'weekday_picker_789', 2, 1),
    (6, 'select', 'text', 'Low;Medium;High;Very High;Extreme', '', 0, 'intensity_level_012', 3, 1),
    (7, 'select', 'text', 'Option A;Option B;Option C;Option D;Option E', '', 0, 'choice_matrix_345', 4, 1),
    (13, 'select', 'text', 'Alpha;Beta;Gamma;Delta;Epsilon;Zeta;Eta;Theta;Iota;Kappa', 'Andere', 0, 'greek_letters_678', 5, 1);
    """

    child_questions_sql = """
    INSERT INTO childquestion (id, component, type, options, additional_option, required, name, "order", visibility) VALUES
    (5, 'select', 'text', 'Yes;No', '', 0, 'binary_choice_567', 2, 1),
    (6, 'select', 'text', 'Yes;No', '', 0, 'confirm_option_890', 3, 1),
    (7, 'select', 'text', 'Yes;No', '', 0, 'toggle_switch_123', 4, 1),
    (8, 'select', 'text', 'Yes;No', '', 0, 'checkbox_item_456', 5, 1),
    (9, 'select', 'text', 'Yes;No', '', 0, 'radio_button_789', 6, 1),
    (10, 'select', 'text', 'Yes;No;Maybe', 'Andere', 0, 'tri_state_012', 7, 1),
    (11, 'select', 'text', 'Yes;No', '', 0, 'flag_status_345', 8, 1),
    (13, 'select', 'text', 'Male;Female;Other', '', 0, 'gender_field_678', 9, 1),
    (17, 'select', 'text', '0;1;2;3;4;5;6;7;8;9;10', '', 0, 'count_input_901', 10, 1),
    (18, 'select', 'text', '0;1;2;3;4;5;6;7;8;9;10', '', 0, 'quantity_box_234', 11, 1),
    (19, 'select', 'text', 'Daily;Weekly;Monthly;Yearly;Never', '', 0, 'frequency_sel_567', 12, 1),
    (20, 'select', 'text', 'Excellent;Good;Fair;Poor;Very Poor', '', 0, 'rating_scale_890', 13, 1),
    (21, 'textarea', 'text', '35;36;37;38;39;40;41;42;43;44;45', '', 0, 'weeks_counter_123', 14, 1),
    (22, 'select', 'text', '0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16', '', 0, 'duration_pick_456', 15, 1);
    """

    session.execute(text(user_questions_sql))
    session.execute(text(child_questions_sql))
    session.commit()


@pytest.fixture(scope="module")
def setup_test_data():
    """Create test directory and verify base data exists"""
    # Verify the base data file exists and has the expected number of rows
    assert os.path.exists(BASE_CSV_PATH), f"Base data file not found at {BASE_CSV_PATH}"
    df = pd.read_csv(
        BASE_CSV_PATH, sep="\t", encoding="utf-16", encoding_errors="replace"
    )
    assert len(df) == 427, f"Base file should contain exactly 427 rows, found {len(df)}"

    # Create test directory if it doesn't exist
    os.makedirs(TEST_DIR, exist_ok=True)

    yield

    # Clean up test directory after all tests
    if os.path.exists(TEST_CSV_PATH):
        os.remove(TEST_CSV_PATH)


@pytest.fixture
def test_csv_file():
    """Create a fresh copy of the base data for each test"""
    try:
        shutil.copy(BASE_CSV_PATH, TEST_CSV_PATH)
        print(f"Successfully copied {BASE_CSV_PATH} to {TEST_CSV_PATH}")
    except Exception as e:
        print(f"Error copying file: {e}")
        # Try to list the directory contents to debug
        try:
            import_data_dir = os.path.dirname(BASE_CSV_PATH)
            print(f"Contents of {import_data_dir}: {os.listdir(import_data_dir)}")
        except Exception as dir_e:
            print(f"Couldn't list directory: {dir_e}")
        raise

    return TEST_CSV_PATH


@pytest_asyncio.fixture
async def import_manager(test_csv_file, session, user_session):
    """Create and configure ImportManager for testing"""
    # Create ImportPaths with test data paths
    import_paths = ImportPaths(
        additional_data_path=test_csv_file, labels_path=LABELS_CSV_PATH
    )

    # For these purposes we deduplicate to avoid unique constraint errors.
    # should not be needed for general test and test DB should be have no import data (only conftest data)
    # await remove_duplicate_cases(test_csv_file, session)
    # logger.debug(f"Removed duplicates from test file {test_csv_file}")

    manager = ImportManager(session=session, user_session=user_session, debug=True)
    manager.data_manager.import_paths = import_paths

    insert_test_questions(session)

    # Run the import
    await manager.run_additional_data_import()

    return manager


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_user_answers_exist(session, setup_test_data, import_manager):
    # Test that answers exist for a random test User which will have been created (with incremental 300 ID because
    # there are >300 chidlren in the data set).
    user_answers = session.exec(
        select(UserAnswer).where(UserAnswer.user_id == 300)
    ).all()

    assert len(user_answers) > 0, "No user answers found for user_id 300"


def locate_child_id_for_case_id(session, case_id):
    child_name = f"Imported Child {case_id}"
    child_result = session.execute(
        select(Child).where(Child.name == child_name)
    ).first()

    if child_result is not None:
        child = child_result[0]
        return child.id


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_answers_for_child_1874(session, setup_test_data, import_manager):
    child_id = locate_child_id_for_case_id(session, "159")

    logger.debug("Child ID found:")
    logger.debug(child_id)

    # Test language answer
    gesundheit_motorik_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id, ChildAnswer.question_id == 5
        )
    ).first()

    print("Determined child ID was:", child_id)

    print(gesundheit_motorik_answer)

    all_child_answers = session.exec(
        select(ChildAnswer).where(ChildAnswer.child_id == child_id)
    ).all()

    print("\nAll answers for child ID", child_id, ":")
    for answer in all_child_answers:
        print(f"Question {answer.question_id}: {answer.answer}")

    assert gesundheit_motorik_answer is not None
    assert gesundheit_motorik_answer.answer == "Nein"  # and not nicht ausgewahlt


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_basic_date_of_birth_correct(
    session, setup_test_data, import_manager
):
    child_id = locate_child_id_for_case_id(session, "159")
    child = session.execute(
        select(Child).where(Child.id == child_id)
    ).scalar_one_or_none()
    assert child.birth_year == 2024
    assert child.birth_month == 9


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_answers_for_child(session, setup_test_data, import_manager):
    child_id = locate_child_id_for_case_id(session, "159")

    # Test yes/no answer
    yes_no_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id, ChildAnswer.question_id == 11
        )
    ).first()

    assert yes_no_answer is not None
    assert yes_no_answer.answer == "Ja"

    # Test gender answer
    gender_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id, ChildAnswer.question_id == 13
        )
    ).first()

    assert gender_answer is not None
    assert gender_answer.answer == "Weiblich"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_answer_with_additional_information(
    session, setup_test_data, import_manager
):
    # Query for UserAnswers where additional_answer is not NULL
    answer_with_additional = session.exec(
        select(UserAnswer).where(
            func.coalesce(UserAnswer.additional_answer, None).isnot(None)
        )
    ).first()

    # Alternative approach - using SQLAlchemy's is_not method
    # answer_with_additional = session.exec(
    #     select(UserAnswer).where(UserAnswer.additional_answer.isnot(None))
    # ).first()

    # Verify we found an answer with additional_answer
    assert answer_with_additional is not None, (
        "No UserAnswer with additional_answer found"
    )
    assert answer_with_additional.additional_answer is not None
    assert len(answer_with_additional.additional_answer) > 0


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_parent_relationship(session, setup_test_data, import_manager):
    # Test that child has correct parent relationship
    child_id = locate_child_id_for_case_id(session, "159")
    child = session.exec(select(Child).where(Child.id == child_id)).first()

    assert child is not None
    assert child.user_id is not None

    # Verify parent has answers
    parent_answers = session.exec(
        select(UserAnswer).where(UserAnswer.user_id == child.user_id)
    ).all()

    assert len(parent_answers) > 0, (
        f"No answers found for parent (user_id: {child.user_id}) of child_id {child_id}"
    )
