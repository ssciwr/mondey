from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pandas as pd

from mondey_backend.import_data.manager.import_manager import ImportManager


def import_manager() -> ImportManager:
    return ImportManager(session=Mock(), user_session=Mock())


def test_pregnancy_answers_are_saved_for_database_child_id():
    manager = import_manager()

    with patch.object(
        manager, "create_answer", return_value=(False, Mock())
    ) as create_answer:
        handled = manager.process_special_answer(
            question_label="Termingebunden?",
            answer="Termingeboren",
            variable="FK03",
            case_id=924,
            db_child_id=42,
        )

    assert handled
    assert create_answer.call_args_list == [
        call(
            user_or_child_id=42,
            question_id=21,
            answer_text="41",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
        call(
            user_or_child_id=42,
            question_id=22,
            answer_text="0",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
    ]


def test_premature_indicator_waits_for_pregnancy_duration():
    manager = import_manager()

    with patch.object(manager, "create_answer") as create_answer:
        handled = manager.process_special_answer(
            question_label="Termingebunden?",
            answer="Frühgeboren",
            variable="FK03",
            case_id=924,
            db_child_id=42,
        )

    assert handled
    create_answer.assert_not_called()


def test_premature_pregnancy_duration_is_parsed_and_saved():
    manager = import_manager()

    with patch.object(
        manager, "create_answer", return_value=(False, Mock())
    ) as create_answer:
        handled = manager.process_special_answer(
            question_label="Frühgeboren: [01]",
            answer="34+3",
            variable="FK04_01",
            case_id=924,
            db_child_id=42,
        )

    assert handled
    assert create_answer.call_args_list == [
        call(
            user_or_child_id=42,
            question_id=21,
            answer_text="34",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
        call(
            user_or_child_id=42,
            question_id=22,
            answer_text="3",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
    ]


def test_import_answers_passes_premature_weeks_text_to_special_handler():
    manager = import_manager()
    child = Mock(name="child")
    child.name = "Imported Child 924"
    child.id = 42
    manager.data_manager.session.exec.return_value.all.return_value = [child]
    manager.data_manager.load_labels_df = Mock(
        return_value=pd.DataFrame(
            [
                {
                    "Variable": "FK03",
                    "Variable Label": "Termingebunden?",
                    "Response Code": 2,
                    "Response Label": "Frühgeboren",
                    "Variable Type": "NOMINAL",
                },
                {
                    "Variable": "FK04_01",
                    "Variable Label": "Frühgeboren: [01]",
                    "Response Code": pd.NA,
                    "Response Label": pd.NA,
                    "Variable Type": "TEXT",
                },
            ],
            index=[171, 172],
        )
    )
    data = pd.DataFrame([{"CASE": 924, "FK03": 2, "FK04_01": "34+3"}])

    with patch.object(
        manager, "create_answer", return_value=(False, Mock())
    ) as create_answer:
        manager.import_answers(data)

    assert create_answer.call_args_list == [
        call(
            user_or_child_id=42,
            question_id=21,
            answer_text="34",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
        call(
            user_or_child_id=42,
            question_id=22,
            answer_text="3",
            set_only_additional_answer=False,
            is_child_question=True,
        ),
    ]


def test_sibling_answer_is_saved_for_database_child_id():
    manager = import_manager()

    with patch.object(
        manager, "create_answer", return_value=(False, Mock())
    ) as create_answer:
        handled = manager.process_special_answer(
            question_label="Jüngere Geschwister",
            answer="2",
            variable="FK10",
            case_id=924,
            db_child_id=42,
        )

    assert handled
    create_answer.assert_called_once_with(
        user_or_child_id=42,
        question_id=18,
        answer_text="2",
        set_only_additional_answer=False,
        is_child_question=True,
    )
