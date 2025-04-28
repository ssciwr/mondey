# todo: This file needs to set Q ID 10 to 12 or 13 I believe too, to make the data line up correctly.

# Otherwise answers point to a non existing old question.

from sqlmodel import select as select

from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.models.questions import ChildAnswer


def merge_andere_diagnosen():
    """
    Merges answers from question ID 12 (Other diagnoses) into the additional_answer field
    of question ID 10 for the same child.
    """
    count_merged = 0
    with get_import_current_session()[0] as session:
        # Get all answers for question ID 12 (Other diagnoses)
        q12_stmt = select(ChildAnswer).where(ChildAnswer.question_id == 12)
        q12_answers = session.exec(q12_stmt).all()

        for q12_answer in q12_answers:
            # Find the corresponding answer for question ID 10 for the same child
            q10_stmt = select(ChildAnswer).where(
                ChildAnswer.child_id == q12_answer.child_id,
                ChildAnswer.question_id == 10,
            )
            q10_answer = session.exec(q10_stmt).first()

            if q10_answer:
                # Append the other diagnosis to the additional_answer field
                if q10_answer.additional_answer:
                    q10_answer.additional_answer += f", {q12_answer.answer}"
                else:
                    q10_answer.additional_answer = q12_answer.answer
                count_merged += 1

        session.commit()
        print("Done!")
        print(f"Merged {count_merged} 'Other diagnoses' answers into question ID 10")

        # todo; DOuble check fi answers for question ID 12 (or I remember in the back of my head 13)
        # remain wrongly in the data.
