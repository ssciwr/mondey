import os
import shutil
import pytest
import pandas as pd
from sqlmodel import select

from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.children import Child
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import UserAnswer

from mondey_backend.import_data.await align_additional_data_to_current_answers import \
    await align_additional_data_to_current_answers

from mondey_backend.import_data.utils import additional_data_path, labels_path

from mondey_backend.import_data.utils import questions_configured_path

# Path constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BASE_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", additional_data_path)
LABELS_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", labels_path)
QUESTIONS_CONFIGURATION_CSV_PATH = os.path.join(PROJECT_ROOT, "src", "mondey_backend", "import_data", questions_configured_path)

# Similarly, update the TEST_DIR path if needed:
TEST_DIR = os.path.join(os.path.dirname(__file__))  # Current directory
TEST_CSV_PATH = os.path.join(TEST_DIR, "test_data.csv")


@pytest.fixture(scope="module")
def setup_test_data():
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

@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_user_answers_exist(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()

    # Test that answers exist for a specific user
    user_answers = import_session.exec(
        select(UserAnswer).where(UserAnswer.user_id == 443)
    ).all()

    assert len(user_answers) > 0, "No user answers found for user_id 443"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_child_answers_for_child_1874(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()
    child_id = 1874

    # Test language answer
    language_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 20
        )
    ).first()

    assert language_answer is not None
    assert language_answer.answer == "Deutsch"

    # Test birth year answer
    birth_year_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 2
        )
    ).first()

    assert birth_year_answer is not None
    assert birth_year_answer.answer == "2021"

    # Test numeric value answer
    numeric_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 17
        )
    ).first()

    assert numeric_answer is not None
    assert numeric_answer.answer == "0"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_child_answers_for_child_1857(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()
    child_id = 1857

    # Test yes/no answer
    yes_no_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 11
        )
    ).first()

    assert yes_no_answer is not None
    assert yes_no_answer.answer == "Ja"

    # Test gender answer
    gender_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == child_id,
            ChildAnswer.question_id == 13
        )
    ).first()

    assert gender_answer is not None
    assert gender_answer.answer == "Weiblich"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_specific_user_answers(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()

    # This is from the original data: checking it is preserved
    job_answer = import_session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 29,
            UserAnswer.question_id == 6
        )
    ).first()

    assert job_answer is not None
    assert job_answer.answer == "Führungskraft 2 (z.B. Vertriebs-/Verkaufsleitung, Führung kleinerer Unternehmen)"

    # Special eltern question
    parent_type_answer = import_session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 283,
            UserAnswer.question_id == 13
        )
    ).first()

    assert parent_type_answer is not None
    assert parent_type_answer.answer == "Leibliche Mutter"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_answer_with_additional_information(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()

    # Find an answer with additional_answer field populated
    answer_with_additional = import_session.exec(
        select(UserAnswer).where(
            UserAnswer.additional_answer != None
        ).limit(1)
    ).first()

    assert answer_with_additional is not None
    assert answer_with_additional.additional_answer is not None
    assert len(answer_with_additional.additional_answer) > 0


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_child_parent_relationship(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()

    # Test that child has correct parent relationship
    child_id = 1874
    child = import_session.exec(
        select(Child).where(Child.id == child_id)
    ).first()

    assert child is not None
    assert child.user_id is not None

    # Verify parent has answers
    parent_answers = import_session.exec(
        select(UserAnswer).where(UserAnswer.user_id == child.user_id)
    ).all()

    assert len(parent_answers) > 0, f"No answers found for parent (user_id: {child.user_id}) of child_id {child_id}"


@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_negative_cases(setup_test_data, test_csv_file):
    await align_additional_data_to_current_answers(data_path=test_csv_file, labelling_path=LABELS_CSV_PATH, questions_configuration_path=QUESTIONS_CONFIGURATION_CSV_PATH)

    import_session, import_engine = get_import_test_session()

    # Test non-existent child ID
    non_existent_child_answer = import_session.exec(
        select(ChildAnswer).where(
            ChildAnswer.child_id == 99999,
            ChildAnswer.question_id == 1
        )
    ).first()

    assert non_existent_child_answer is None

    # Test non-existent user ID
    non_existent_user_answer = import_session.exec(
        select(UserAnswer).where(
            UserAnswer.user_id == 99999,
            UserAnswer.question_id == 1
        )
    ).first()

    assert non_existent_user_answer is None
