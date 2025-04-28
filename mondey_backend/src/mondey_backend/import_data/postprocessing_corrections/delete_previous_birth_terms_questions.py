from sqlmodel import select
from sqlmodel import text

from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText


def delete_previous_birth_terms_questions(dry_run=False):
    """
    Delete the original questions (IDs 3 and 4) and their associated answers.

    Args:
        dry_run: If True, don't commit changes to the database
    """
    question_ids_to_delete = [3, 4]  # Termingeboren/Fruhgeboren and Fruhgeboren [01]

    with get_import_current_session()[0] as session:
        # Count records before deletion for reporting
        answer_count = 0
        for q_id in question_ids_to_delete:
            answers = session.exec(
                select(ChildAnswer).where(ChildAnswer.question_id == q_id)
            ).all()
            answer_count += len(answers)

        print(
            f"Found {answer_count} answers to delete for question IDs {question_ids_to_delete}"
        )

        if not dry_run:
            # 1. Delete all child answers for these questions
            for q_id in question_ids_to_delete:
                # First get count for reporting
                answers = session.exec(
                    select(ChildAnswer).where(ChildAnswer.question_id == q_id)
                ).all()
                print(f"Deleting {len(answers)} answers for question ID {q_id}")

                # Then delete
                session.exec(
                    text(f"DELETE FROM childanswer WHERE question_id = {q_id}")
                )
                print(f"Deleted answers for question ID {q_id}")

            # 2. Delete the question texts for these questions
            for q_id in question_ids_to_delete:
                # First get count for reporting
                question_texts = session.exec(
                    select(ChildQuestionText).where(
                        ChildQuestionText.child_question_id == q_id
                    )
                ).all()
                print(
                    f"Deleting {len(question_texts)} question texts for question ID {q_id}"
                )

                # Then delete
                session.exec(
                    text(
                        f"DELETE FROM childquestiontext WHERE child_question_id = {q_id}"
                    )
                )
                print(f"Deleted question texts for question ID {q_id}")

            # 3. Delete the questions themselves
            for q_id in question_ids_to_delete:
                question = session.exec(
                    select(ChildQuestion).where(ChildQuestion.id == q_id)
                ).first()

                if question:
                    print(f"Deleting question: {q_id} - {question.name}")
                    session.exec(text(f"DELETE FROM childquestion WHERE id = {q_id}"))
                    print(f"Deleted question ID {q_id}")
                else:
                    print(f"Question ID {q_id} not found")

            # Commit all changes
            session.commit()
            print("All deletions committed to database")
        else:
            print("[DRY RUN] Would delete:")
            print(f"- {answer_count} answers for question IDs {question_ids_to_delete}")

            for q_id in question_ids_to_delete:
                question_texts = session.exec(
                    select(ChildQuestionText).where(
                        ChildQuestionText.child_question_id == q_id
                    )
                ).all()
                print(f"- {len(question_texts)} question texts for question ID {q_id}")

                question = session.exec(
                    select(ChildQuestion).where(ChildQuestion.id == q_id)
                ).first()
                if question:
                    print(f"- Question: {q_id} - {question.name}")
                else:
                    print(f"- Question ID {q_id} (not found)")

            print("[DRY RUN] No changes committed to database")

    print("Delete operation completed")
