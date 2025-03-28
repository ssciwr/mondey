import pytest
from sqlmodel import select

from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.models.children import Child
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestionText


# This passes after running `import_all.py true`
@pytest.mark.skip(reason="Requires actual data CSVs which are not present")
def test_andere_freetext_answer_is_saved_for_main_question():
    import_session, import_engine = get_import_test_session()
    # This focuses on the fact that the "Andere" question should not be their own question/answer but should be
    # merged into the questions with the labelled ordinary select option answers
    # This will make sure these freetext questions answers are both recorded correctly, and any children added to the
    # data in the interface will have a comparable format, not a difference with freetext "other" answers.
    CASE_ID_other_ages = 222
    expected_answer_other_ages = "28+6"
    variable_other_ages = "FK04_01"
    question_part_other_ages = "Frühgeboren: [01]"
    question_text_other_ages = variable_other_ages + ": " + question_part_other_ages

    # Test Case 2: Nationality Answer (this one is also an "Other" question, but it's for parents, so USerAnswer)
    CASE_ID = 202
    variable = "FE02"
    question_part = "Staatsangehörigkeit"
    # question_full = "Andere Staatsangehörigkeit: [01]"
    question_text_to_match_with_user_question_text = variable + ": " + question_part
    expected_answer = "Österreich"

    def get_question_id(import_session, text):
        question_text = import_session.exec(
            select(ChildQuestionText).where(ChildQuestionText.question == text)
        ).first()
        print("Searching for text:", text, ":")

        if not question_text:
            question_text = import_session.exec(
                select(UserQuestionText).where(UserQuestionText.question == text)
            ).first()
            if not question_text:
                raise ValueError(f"No child OR parent question found with text: {text}")

        # Modify this part to return the correct ID based on the object type
        if hasattr(question_text, "child_question_id"):
            return question_text.child_question_id
        elif hasattr(question_text, "user_question_id"):
            return question_text.user_question_id
        else:
            raise ValueError(f"Unable to find ID for question text: {text}")

    # Test 1: Saving answer for Frühgeboren question
    question_id_other_ages = get_question_id(import_session, question_text_other_ages)

    # Verify the answer was saved correctly
    saved_answer_other_ages = import_session.execute(
        select(ChildAnswer).where(
            ChildAnswer.child_id == CASE_ID_other_ages,
            ChildAnswer.question_id == question_id_other_ages,
        )
    ).scalar_one_or_none()

    print("Saved answer other ages was: ", saved_answer_other_ages)
    print("Child ID:", CASE_ID_other_ages, "question ID:", question_id_other_ages)
    # Todo: Before this was passing. Now it isn't, because no answers for question ID 4 are being saved
    # (or are they? is lack of answers because most children have an empty field there?)
    # Answer: No, becuase SELECT * FROM childanswer WHERE question_id=4 returns nothing...
    # I think all answers are being dsicarded, because the question can't be found when the code goes to save
    # the answers.
    assert saved_answer_other_ages is not None
    assert saved_answer_other_ages.answer == expected_answer_other_ages

    # Test 2: Saving answer for Nationality question
    question_id = get_question_id(
        import_session, question_text_to_match_with_user_question_text
    )

    def get_parent_of_child(child_id):
        print("Child ID: ", child_id)
        child = import_session.execute(
            select(Child).where(Child.id == child_id)
        ).scalar_one_or_none()

        if not child:
            raise ValueError("Child could not be found")

        print("Childs user ID was: ", child.user_id)
        return child.user_id

    user_id = get_parent_of_child(CASE_ID)

    saved_answer = import_session.execute(
        select(UserAnswer)
        .where(UserAnswer.user_id == user_id)
        .where(UserAnswer.question_id == question_id)
    ).scalar_one_or_none()

    print("Saved answer was: ", saved_answer)
    print("Looked up user ID: ", user_id, " and question ID: ", question_id)
    assert saved_answer is not None
    assert saved_answer.answer == "Andere"
    assert saved_answer.additional_answer == expected_answer

    # Negative Test Case: Verify no answer for a non-existent scenario
    non_existent_answer = import_session.execute(
        select(ChildAnswer).where(
            ChildAnswer.child_id
            == 99999999999,  # Non-existent child ID, till we get to the next galaxy, anyway
            ChildAnswer.question_id == 999999999999,  # Non-existent question ID
        )
    ).scalar_one_or_none()
    print("Non existent answer: ", non_existent_answer)
    assert non_existent_answer is None


# todo: Ideally, add a test which asserts that independent free texts also have their answers (questions without a
# select type, so actually pure free text question-answers)
# *FK04_01: Frühgeboren: [01] + Andere Diagnosen are good examples of that.
