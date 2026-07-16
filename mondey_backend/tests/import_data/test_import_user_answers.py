from unittest.mock import Mock
from unittest.mock import patch

import pandas as pd

from mondey_backend.import_data.manager.import_manager import ImportManager


def test_import_answers_saves_respondent_birth_year():
    manager = ImportManager(session=Mock(), user_session=Mock())
    child = Mock(name="child")
    child.name = "Imported Child 924"
    child.id = 42
    question = Mock(name="question")
    question.id = 2
    query_result = manager.data_manager.session.exec.return_value
    query_result.all.return_value = [child]
    query_result.first.return_value = question
    manager.data_manager.load_labels_df = Mock(
        return_value=pd.DataFrame(
            [
                {
                    "Variable": "FE01",
                    "Variable Label": "Geburtsjahr",
                    "Response Code": 43,
                    "Response Label": "1991",
                    "Variable Type": "NOMINAL",
                }
            ],
            index=[171],
        )
    )
    data = pd.DataFrame([{"CASE": 924, "FE01": 43}])

    with (
        patch.object(manager, "get_childs_parent_id", return_value=7),
        patch.object(
            manager, "create_answer", return_value=(False, Mock())
        ) as create_answer,
    ):
        manager.import_answers(data)

    create_answer.assert_called_once_with(
        user_or_child_id=7,
        question_id=2,
        answer_text="1991",
        set_only_additional_answer=False,
        is_child_question=False,
    )
