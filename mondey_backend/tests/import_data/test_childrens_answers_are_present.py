from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.src.mondey_backend.models.questions import UserAnswer


def test_andere_freetext_answer_is_saved_for_main_question(session):
    # This focuses on the fact that the "Andere" question should not be their own question/answer but should be
    # merged into the questions with the labelled ordinary select option answers
    # This will make sure these freetext questions answers are both recorded correctly, and any children added to the
    # data in the interface will have a comparable format, not a difference with freetext "other" answers.
    CASE_ID_other_ages = 222
    expected_answer_other_ages = "28+6"
    variable_other_ages = "FK04_01"
    question_part_other_ages = "Frühgeboren"
    question_text_other_ages = variable_other_ages + ": " + question_part_other_ages

    # Test Case 2: Nationality Answer (this one is also an "Other" question, but it's for parents, so USerAnswer)
    CASE_ID = 202
    variable = "FE03_01"
    question_part = "Andere Staatsangehörigkeit: [01]"
    question_text_to_match_with_user_question_text = variable + ": " + question_part
    expected_answer = "Österreich"

    def get_question_id(session, question_text):
        # Look up the child question ID based on the question text
        question_text = (
            session.query(ChildQuestionText)
            .filter(ChildQuestionText.question == question_text)
            .first()
        )

        if not question_text:
            question_text = (
                session.query(ChildQuestionText)
                .filter(ChildQuestionText.question == question_text)
                .first()
            )
            if not question_text:
                raise ValueError(
                    f"No child OR parent question found with text: {question_text}"
                )

        return question_text.child_question_id

    # Test 1: Saving answer for Frühgeboren question
    question_id_other_ages = get_question_id(session, question_text_other_ages)

    child_answer_other_ages = ChildAnswer(
        child_id=CASE_ID_other_ages,
        question_id=question_id_other_ages,
        answer=expected_answer_other_ages,
    )
    session.add(child_answer_other_ages)
    session.commit()

    # Verify the answer was saved correctly
    saved_answer_other_ages = (
        session.query(ChildAnswer)
        .filter(
            ChildAnswer.child_id == CASE_ID_other_ages,
            ChildAnswer.question_id == question_id_other_ages,
        )
        .first()
    )

    assert saved_answer_other_ages is not None
    assert saved_answer_other_ages.answer == expected_answer_other_ages

    # Test 2: Saving answer for Nationality question
    question_id = get_question_id(
        session, question_text_to_match_with_user_question_text
    )

    # user_id = get_parent_of_child(CASE_ID)
    user_id = 1

    user_answer = UserAnswer(
        user_id=user_id, question_id=question_id, answer=expected_answer
    )
    session.add(user_answer)
    session.commit()

    # Verify the answer was saved correctly
    saved_answer = (
        session.query(UserAnswer)
        .filter(UserAnswer.child_id == CASE_ID, UserAnswer.question_id == question_id)
        .first()
    )

    assert saved_answer is not None
    assert saved_answer.answer == expected_answer

    # Negative Test Case: Verify no answer for a non-existent scenario
    non_existent_answer = (
        session.query(ChildAnswer)
        .filter(
            ChildAnswer.child_id
            == 99999999999,  # Non-existent child ID, till we get to the next galaxy, anyway
            ChildAnswer.question_id == 999999999999,  # Non-existent question ID
        )
        .first()
    )

    assert non_existent_answer is None
