import asyncio
import os
import shutil
import pytest
import pytest_asyncio  # Import this for newer versions
import pandas as pd
from sqlmodel import select

from mondey_backend.models.children import Child
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import UserAnswer

from mondey_backend.import_data.manager.import_manager import ImportManager
from mondey_backend.import_data.manager.data_manager import ImportPaths

# Path constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BASE_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", "additional_data_full_backup.csv")
LABELS_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", "labels.csv")
QUESTIONS_CONFIGURATION_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", "questions_configured.csv")

# Test directory
TEST_DIR = os.path.join(os.path.dirname(__file__))  # Current directory
TEST_CSV_PATH = os.path.join(TEST_DIR, "test_data.csv")


# async test

# Create a minimal test to check if async is working
@pytest.mark.asyncio
async def test_minimal_async():
    """Test basic async functionality"""
    await asyncio.sleep(0.1)
    assert True

# For newer versions of pytest-asyncio, use this decorator
@pytest_asyncio.fixture
async def async_fixture():
    await asyncio.sleep(0.1)
    return "test_value"

@pytest.mark.asyncio
async def test_with_async_fixture(async_fixture):
    """Test async fixture"""
    value = async_fixture  # This should now be the resolved value
    assert value == "test_value"

@pytest.fixture(scope="module")
def setup_test_data():
    # todo: Problem here is that our code edits the CSV in place.
    # Which is a bad code smell really. Maybe fix it editing the CSV in place before fixing these tests?
    """Create test directory and verify base data exists"""
    # Verify the base data file exists and has the expected number of rows
    assert os.path.exists(BASE_CSV_PATH), f"Base data file not found at {BASE_CSV_PATH}"
    df = pd.read_csv(BASE_CSV_PATH, sep="\t", encoding="utf-16", encoding_errors="replace")
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
async def import_manager(test_csv_file):
    """Create and configure ImportManager for testing"""
    # Create ImportPaths with test data paths
    import_paths = ImportPaths(
        additional_data_path=test_csv_file,
        labels_path=LABELS_CSV_PATH,
        questions_configured_path=QUESTIONS_CONFIGURATION_CSV_PATH,
    )

    # Create ImportManager with custom paths
    manager = ImportManager(debug=True)
    manager.data_manager.import_paths = import_paths

    # Run the import
    await manager.run_additional_data_import()

    return manager


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_user_answers_exist(session, setup_test_data, import_manager):
    # Test that answers exist for a specific user
    user_answers = session.exec(
        select(UserAnswer).where(UserAnswer.user_id == 443)
    ).all()

    assert len(user_answers) > 0, "No user answers found for user_id 443"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_answers_for_child_1874(session, setup_test_data, import_manager):
    child_id = 1874

    # Test language answer
    language_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 20
        )
    ).first()

    assert language_answer is not None
    assert language_answer.answer == "Deutsch"

    # Test birth year answer
    birth_year_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 2
        )
    ).first()

    assert birth_year_answer is not None
    assert birth_year_answer.answer == "2021"

    # Test numeric value answer
    numeric_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 17
        )
    ).first()

    assert numeric_answer is not None
    assert numeric_answer.answer == "0"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_answers_for_child_1857(session, setup_test_data, import_manager):
    child_id = 1857

    # Test yes/no answer
    yes_no_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 11
        )
    ).first()

    assert yes_no_answer is not None
    assert yes_no_answer.answer == "Ja"

    # Test gender answer
    gender_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 13
        )
    ).first()

    assert gender_answer is not None
    assert gender_answer.answer == "Weiblich"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_specific_user_answers(session, setup_test_data, import_manager):
    # This is from the original data: checking it is preserved
    job_answer = session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 29,
            UserAnswer.question_id == 6
        )
    ).first()

    assert job_answer is not None
    assert job_answer.answer == "Führungskraft 2 (z.B. Vertriebs-/Verkaufsleitung, Führung kleinerer Unternehmen)"

    # Special eltern question
    parent_type_answer = session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 283,
            UserAnswer.question_id == 13
        )
    ).first()

    assert parent_type_answer is not None
    assert parent_type_answer.answer == "Leibliche Mutter"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_answer_with_additional_information(session, setup_test_data, import_manager):
    # Find an answer with additional_answer field populated
    answer_with_additional = session.exec(
        select(UserAnswer).where(
            UserAnswer.additional_answer != None
        ).limit(1)
    ).first()

    assert answer_with_additional is not None
    assert answer_with_additional.additional_answer is not None
    assert len(answer_with_additional.additional_answer) > 0


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_child_parent_relationship(session, setup_test_data, import_manager):
    # Test that child has correct parent relationship
    child_id = 1874
    child = session.exec(
        select(Child).where(Child.id == child_id)
    ).first()

    assert child is not None
    assert child.user_id is not None

    # Verify parent has answers
    parent_answers = session.exec(
        select(UserAnswer).where(UserAnswer.user_id == child.user_id)
    ).all()

    assert len(parent_answers) > 0, f"No answers found for parent (user_id: {child.user_id}) of child_id {child_id}"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
@pytest.mark.asyncio
async def test_negative_cases(session, setup_test_data, import_manager):
    # Test non-existent child ID
    non_existent_child_answer = session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == 99999,
            ChildAnswer.question_id == 1
        )
    ).first()

    assert non_existent_child_answer is None

    # Test non-existent user ID
    non_existent_user_answer = session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 99999,
            UserAnswer.question_id == 1
        )
    ).first()

    assert non_existent_user_answer is None