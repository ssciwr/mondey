from unittest.mock import Mock
from unittest.mock import patch

import pandas as pd
import pytest

from mondey_backend.import_data.manager.import_manager import ImportManager


@pytest.mark.parametrize(
    (
        "variable",
        "variable_label",
        "question_id",
        "is_child_question",
        "answer_text",
    ),
    [
        (
            "FK06_01",
            "Andere Diagnosen: [01]",
            10,
            True,
            "Zöliakie",
        ),
        (
            "FE03_01",
            "Andere Staatsangehörigkeit: [01]",
            3,
            False,
            "Österreich",
        ),
        (
            "FE05_01",
            "Andere Muttersprache: [01]",
            4,
            False,
            "Polnisch",
        ),
    ],
)
def test_import_answers_saves_other_free_text(
    variable,
    variable_label,
    question_id,
    is_child_question,
    answer_text,
):
    manager = ImportManager(session=Mock(), user_session=Mock())
    child = Mock(name="child")
    child.name = "Imported Child 924"
    child.id = 42
    question = Mock(name="question")
    question.id = question_id
    query_result = manager.data_manager.session.exec.return_value
    query_result.all.return_value = [child]
    query_result.first.return_value = question
    manager.data_manager.load_labels_df = Mock(
        return_value=pd.DataFrame(
            [
                {
                    "Variable": variable,
                    "Variable Label": variable_label,
                    "Response Code": pd.NA,
                    "Response Label": pd.NA,
                    "Variable Type": "TEXT",
                }
            ],
            index=[171],
        )
    )
    data = pd.DataFrame([{"CASE": 924, variable: answer_text}])

    with (
        patch.object(manager, "get_childs_parent_id", return_value=7),
        patch.object(
            manager, "create_answer", return_value=(True, Mock())
        ) as create_answer,
    ):
        manager.import_answers(data)

    create_answer.assert_called_once_with(
        user_or_child_id=42 if is_child_question else 7,
        question_id=question_id,
        answer_text=answer_text,
        set_only_additional_answer=True,
        is_child_question=is_child_question,
    )
