import json

from sqlalchemy import delete
from sqlmodel import col
from sqlmodel import select

from mondey_backend.dependencies import get_session
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText


def combine_question_options():
    with next(get_session()) as session:
        # Step 1: Find the question IDs for FP01, FP02, FP04, FP05 (exclude FP03)
        target_questions = ["Mütter", "Väter", "Andere Verwandte", "Fremdbetreuung"]
        eltern_question = "Eltern"

        # Get question IDs by matching the question text in UserQuestionText
        question_ids = []
        for question_text in target_questions:
            stmt = select(UserQuestionText).where(
                UserQuestionText.question == question_text
            )
            text_entries = session.exec(stmt).all()
            for entry in text_entries:
                question_ids.append(entry.user_question_id)

        # Make question_ids unique
        question_ids = list(set(question_ids))
        print("Relevant IDs of questions to remove:", question_ids)

        # Also get FP03 ID for later deletion
        stmt_eltern = select(UserQuestionText).where(
            UserQuestionText.question == eltern_question
        )
        eltern_text = session.exec(stmt_eltern).first()
        eltern_id = eltern_text.user_question_id if eltern_text else None

        # Step 2: Get language IDs to maintain language variants
        stmt_langs = (
            select(UserQuestionText.lang_id)
            .distinct()
            .where(UserQuestionText.user_question_id.in_(question_ids))
        )
        lang_ids = session.exec(stmt_langs).all()

        # Step 3: For each language, combine options from all questions
        combined_options_by_lang = {}

        for lang_id in lang_ids:
            all_options = []

            # Get options for each question in this language
            for question_id in question_ids:
                stmt = select(UserQuestionText).where(
                    (UserQuestionText.user_question_id == question_id)
                    & (UserQuestionText.lang_id == lang_id)
                )
                question_text = session.exec(stmt).first()

                if question_text and question_text.options_json:
                    options = json.loads(question_text.options_json)
                    all_options.extend(options)

            # Create unique options list with sequential values
            seen_names = set()
            unique_options = []
            value_counter = 1.0

            for option in all_options:
                name = option.get("name")
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_options.append(
                        {"value": str(value_counter), "name": name, "disabled": False}
                    )
                    value_counter += 1.0

            # Sort options
            unique_options.sort(key=lambda x: x["name"])

            # Store for this language
            combined_options_json = json.dumps(unique_options)
            options_text = ", ".join([opt["name"] for opt in unique_options])
            combined_options_by_lang[lang_id] = {
                "json": combined_options_json,
                "text": options_text,
            }

        # Step 4: Create a new combined question
        new_question = UserQuestion(
            order=0,
            component="select",
            type="text",
            options="",
            additional_option="",
            required=False,
        )
        session.add(new_question)
        session.flush()  # Get the new ID

        # Step 5: Create text entries for each language
        for lang_id, options_data in combined_options_by_lang.items():
            new_text = UserQuestionText(
                user_question_id=new_question.id,
                lang_id=lang_id,
                question="FP00: Combined Caregivers",  # Question text goes here
                options_json=options_data["json"],
                options=options_data["text"],
            )
            session.add(new_text)

        # Step 6: Record IDs to be deleted (including FP03)
        ids_to_delete = question_ids.copy()
        if eltern_id:
            ids_to_delete.append(eltern_id)

        # Step 7: Commit changes to ensure new question is stored
        session.commit()

        return new_question.id, ids_to_delete


def update_user_answers(new_question_id: int, old_question_ids: list[int]):
    with next(get_session()) as session:
        # Find the FP03 question ID (Eltern)
        stmt = select(UserQuestionText).where(
            UserQuestionText.question == "FP03: Eltern"
        )
        eltern_text = session.exec(stmt).first()
        eltern_id = eltern_text.user_question_id if eltern_text else None

        if eltern_id:
            # Step 1: Delete answers to FP03 (Eltern) question
            stmt_delete = delete(UserAnswer).where(UserAnswer.question_id == eltern_id)
            result = session.execute(stmt_delete)
            deleted_count = result.rowcount
            print(f"Deleted {deleted_count} answers from FP03: Eltern")

        # Step 2: Get all other question IDs that need to be updated (excluding FP03)
        update_ids = [id for id in old_question_ids if id != eltern_id]

        # Step 3: Handle answers one by one to avoid constraint violations
        # First get all users who answered these questions
        stmt_users = (
            select(UserAnswer.user_id)
            .distinct()
            .where(col(UserAnswer.question_id).in_(update_ids))
        )
        users = session.exec(stmt_users).all()

        updated_count = 0
        # For each user, process their answers
        for user_id in users:
            print("Processing user:", user_id)
            # Get all answers for this user for the questions we're combining
            stmt_answers = select(UserAnswer).where(
                (UserAnswer.user_id == user_id)
                & (col(UserAnswer.question_id).in_(update_ids))
            )
            answers = session.exec(stmt_answers).all()

            if not answers:
                continue

            # Find the most appropriate answer to keep (prioritize non-empty answers)
            # This is a simple strategy - you might want a more sophisticated approach
            best_answer = None
            for answer in answers:
                print("Checking answer:", answer)
                if not best_answer or (answer.answer and not best_answer.answer):
                    best_answer = answer

            if best_answer:
                print("Best answer found!", best_answer)

                # Update this one answer to point to the new question
                best_answer.question_id = new_question_id
                print("Pointing it's question ID to", new_question_id)
                session.add(best_answer)
                updated_count += 1

                # Delete the rest of this user's answers for these questions
                for answer in answers:
                    if answer is not best_answer:
                        print("Deleting answer not used: ", answer)
                        session.delete(answer)

        # Step 4: Delete old questions and their text entries
        # First delete text entries
        for old_id in old_question_ids:
            print("Deleting question ID:", old_id)
            stmt_delete_text = delete(UserQuestionText).where(
                col(UserQuestionText.user_question_id) == old_id
            )
            session.execute(stmt_delete_text)

        # Then delete questions
        stmt_delete_questions = delete(UserQuestion).where(
            col(UserQuestion.id).in_(old_question_ids)
        )
        print("Also deleted question IDs:", old_question_ids)
        result = session.execute(stmt_delete_questions)
        deleted_questions = result.rowcount
        print(f"Deleted {deleted_questions} old questions")

        # Commit all changes
        session.commit()

        return {
            "deleted_answers": deleted_count if eltern_id else 0,
            "updated_answers": updated_count,
            "deleted_questions": deleted_questions,
        }


def merge_eltern_question():
    # Execute the functions in sequence
    print("Starting data migration...")
    new_id, old_ids = combine_question_options()
    print(f"Created new combined question with ID {new_id}")

    stats = update_user_answers(new_id, old_ids)

    print("\nData migration completed successfully!")
    print(f"- Created new combined caregiver question with ID {new_id}")
    print(f"- Deleted {stats['deleted_answers']} answers to FP03: Eltern")
    print(f"- Updated {stats['updated_answers']} answers to point to the new question")
    print(f"- Deleted {stats['deleted_questions']} old questions")
