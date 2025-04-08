from sqlmodel import select as sqlmodel_select

from mondey_backend.dependencies import get_session
from mondey_backend.models.questions import ChildAnswer


def merge_andere_diagnosen():
    """
    Merges answers from question ID 12 (Other diagnoses) into the additional_answer field
    of question ID 10 for the same child.
    """
    count_merged = 0
    with next(get_session()) as session:
        # Get all answers for question ID 12 (Other diagnoses)
        q12_stmt = sqlmodel_select(ChildAnswer).where(ChildAnswer.question_id == 12)
        q12_answers = session.exec(q12_stmt).all()

        for q12_answer in q12_answers:
            # Find the corresponding answer for question ID 10 for the same child
            q10_stmt = sqlmodel_select(ChildAnswer).where(
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


if __name__ == "__main__":
    merge_andere_diagnosen()
