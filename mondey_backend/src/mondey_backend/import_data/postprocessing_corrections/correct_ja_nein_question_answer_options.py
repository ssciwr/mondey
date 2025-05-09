from sqlmodel import select as select

from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText

term_not_chosen = "nicht gewählt"
term_chosen = "ausgewählt"


def correct_ja_nein_question_answer_options():
    print("Changing ja/nein answers...")
    count_changed = 0
    import_session, engine = get_import_current_session()
    with import_session as session:
        user_questions_texts = session.exec(select(UserQuestionText)).all()
        child_questions_texts = session.exec(select(ChildQuestionText)).all()
        all_questions = [*user_questions_texts, *child_questions_texts]
        print("Questions we will check for updating:", len(all_questions))
        for question in all_questions:
            debug = False
            # update options, options_json
            # Better than an UPDATE with LIKE etc matching for this many answers
            if question.question == "Geschwister?: Ja, jüngere Geschwister":
                debug = True

            if debug:
                print(question)
            question.options = (
                question.options.replace(term_not_chosen, "Nein")
                .replace(term_chosen, "Ja")
                .replace("ausgew\\u00e4hlt", "Ja")
                .replace("nicht gew\\u00e4hlt", "Nein")
            )

            question.options_json = (
                question.options_json.replace(term_not_chosen, "Nein")
                .replace(term_chosen, "Ja")
                .replace("ausgew\\u00e4hlt", "Ja")
                .replace("nicht gew\\u00e4hlt", "Nein")
            )

            if debug:
                print("After:")
                print(question.options_json)

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
        all_answers = [*user_answers, *child_answers]

        print("Answers we will check for updating:", len(all_answers))
        for answer in all_answers:
            original_answer = answer.answer
            answer.answer = answer.answer.replace(term_chosen, "Ja").replace(
                term_not_chosen, "Nein"
            )
            if original_answer != answer.answer:
                count_changed += 1

        session.commit()
        print("Done!")
        print("Changed this many answers(and further questions):", count_changed)
