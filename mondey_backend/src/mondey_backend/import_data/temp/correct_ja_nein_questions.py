from sqlmodel import select as select

from mondey_backend.dependencies import get_session
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText

term_not_chosen = "nicht gewählt"
term_chosen = "ausgewählt"


def replace_answer_terms():
    count_changed = 0
    with next(get_session()) as session:
        user_questions_texts = session.exec(select(UserQuestionText)).all()
        child_questions_texts = session.exec(select(ChildQuestionText)).all()

        for question in [*user_questions_texts, *child_questions_texts]:
            # update options, options_json
            # Better than an UPDATE with LIKE etc matching for this many answers
            question.options = question.options.replace(
                term_not_chosen, "Nein"
            ).replace(term_chosen, "Ja")
            question.options_json = question.options_json.replace(
                term_not_chosen, "Nein"
            ).replace(term_chosen, "Ja")

        user_questions = session.exec(select(UserQuestion)).all()
        child_questions = session.exec(select(ChildQuestion)).all()
        for question in [*user_questions, *child_questions]:
            question.options = question.options.replace(
                term_not_chosen, "Nein"
            ).replace(term_chosen, "Ja")

        # Only if questions changed without error update the answers...
        stmt = select(UserAnswer)
        child_stmt = select(ChildAnswer)
        user_answers = session.exec(stmt).all()
        child_answers = session.exec(child_stmt).all()
        for answer in [*user_answers, *child_answers]:
            original_answer = answer.answer
            answer.answer = answer.answer.replace(term_chosen, "Ja").replace(
                term_not_chosen, "Nein"
            )
            if original_answer != answer.answer:
                count_changed += 1

        session.commit()
        print("Done!")
        print("Changed this many answers(and further questions):", count_changed)


replace_answer_terms()
