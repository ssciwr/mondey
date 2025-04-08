from sqlmodel import select as sqlmodel_select

from mondey_backend.dependencies import get_session
from mondey_backend.models.questions import UserAnswer


def remove_encoding_in_text_answers():
    count_changed = 0
    with next(get_session()) as session:
        stmt = sqlmodel_select(UserAnswer)
        child_stmt = sqlmodel_select(UserAnswer)
        user_answers = session.exec(stmt).all()
        child_answers = session.exec(child_stmt).all()
        for answer in [*user_answers, *child_answers]:
            original_answer = answer.answer
            answer.answer = answer.answer.replace("&#44;", ",").replace("<tab>", " ")
            if original_answer != answer.answer:
                count_changed += 1

        session.commit()
        print("Done!")
        print("Changed this many answers:", count_changed)


remove_encoding_in_text_answers()
