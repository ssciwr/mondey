"""

Right now the data includes two questions that are related:
Fruhgeboren [01]: Will be a number of weeks, like "38", or "39". Sometimes it includes an annex amount of weeks, with
either a comma, or a + separating the two. For example, "34+4" or "34, 3" or "34 +3"

The highest value given in Fruhgeboren was 40 weeks.

ID 3 = "Termingeboren" or "Fruhgeboren" (select multiple choice option)
ID 4 = the sometimes present Fruhgeboren [01] field which when present denotes the weeks of early birth and any incubator time.


Now what we want to do is combine these two into the following:
A question on "weeks of birth", where 41 will be the same as"Termingeboren" (born normally).
A separate question on "weeks in incubator" with default value 0. If the answer to Fruhgeboren for that child has "+" or
"," annex of weeks, than this answer will have that value.

I used Claude to write parts of this script based on the above and my basic outline as a prompt.
"""

import json

from sqlmodel import select as select

from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText


def parse_weeks(birth_term):
    # Handle empty or None values
    if not birth_term or birth_term == "<null>":
        return (0, 0)

    # Clean the input string
    birth_term = birth_term.strip()

    # Check for "+" or "," separator indicating incubator weeks
    separators = ["+", ","]
    for sep in separators:
        if sep in birth_term:
            parts = [p.strip() for p in birth_term.split(sep)]
            try:
                birth_weeks = int(parts[0])
                incubator_weeks = int(parts[1])
                return (birth_weeks, incubator_weeks)
            except (ValueError, IndexError):
                print(f"Warning: Could not parse '{birth_term}' with separator '{sep}'")

    # If no separator found, assume it's just the birth weeks
    try:
        birth_weeks = int(birth_term)
        return (birth_weeks, 0)
    except ValueError:
        print(f"Warning: Could not parse '{birth_term}' as an integer")
        return (0, 0)


def transform_birth_terms(dry_run=False):
    """
    Transform birth terms data from the old format to the new format.

    Args:
        dry_run: If True, don't commit changes to the database
    """
    stats = {
        "total_records": 0,
        "termingeboren_count": 0,
        "fruhgeboren_count": 0,
        "with_incubator_weeks": 0,
        "without_birth_info": 0,
        "processing_errors": 0,
    }

    with get_import_current_session()[0] as session:
        # 1. Find or create the new questions
        # Check if questions with appropriate names already exist
        birth_question = session.exec(
            select(ChildQuestion).where(ChildQuestion.name == "Schwangerschaftsdauer")
        ).first()

        incubator_question = session.exec(
            select(ChildQuestion).where(ChildQuestion.name == "Inkubatorwochen")
        ).first()

        # If questions don't exist, create them
        if not birth_question or not incubator_question:
            if not birth_question:
                # Create options for select from 26 to 41 (with 41 being Termingeboren)
                birth_options = []
                options_json = []

                # Add options for weeks 26-40
                for week in range(26, 41):
                    birth_options.append(str(week))
                    options_json.append({"value": str(week), "name": str(week)})

                # Add Termingeboren as option 41
                birth_options.append("41")
                options_json.append({"value": "41", "name": "Termingeboren"})

                birth_options_str = ";".join(birth_options)
                birth_options_json = json.dumps(options_json)

                birth_question = ChildQuestion(
                    order=0,
                    component="select",
                    type="select",
                    options=birth_options_str,
                    additional_option="",
                    required=True,
                    name="birth_weeks",
                )

                if not dry_run:
                    session.add(birth_question)
                    print(f"Created birth_weeks question with ID: {birth_question.id}")

                    # Add question texts for each language
                    languages = session.exec(
                        select(ChildQuestionText.lang_id).distinct()
                    ).all()
                    for lang in languages:
                        question_text = ChildQuestionText(
                            child_question_id=birth_question.id,
                            lang_id=lang,
                            question="Geburtswochen",
                            options_json=birth_options_json,
                            options=birth_options_str,
                        )
                        session.add(question_text)
                else:
                    print(
                        f"[DRY RUN] Would create birth_weeks question with ID: {birth_question.id}"
                    )

            if not incubator_question:
                incubator_question = ChildQuestion(
                    order=0,
                    component="textarea",
                    type="textarea",
                    options="",
                    additional_option="",
                    required=True,
                    name="incubator_weeks",
                )

                if not dry_run:
                    session.add(incubator_question)
                    print(
                        f"Created incubator_weeks question with ID: {incubator_question.id}"
                    )

                    # Add question texts for each language
                    languages = session.exec(
                        select(ChildQuestionText.lang_id).distinct()
                    ).all()
                    for lang in languages:
                        question_text = ChildQuestionText(
                            child_question_id=incubator_question.id,
                            lang_id=lang,
                            question="Inkubatorwochen",
                            options_json="",
                            options="",
                        )
                        session.add(question_text)
                else:
                    print(
                        f"[DRY RUN] Would create incubator_weeks question with ID: {incubator_question.id}"
                    )

        # 2. Process all children
        # Get all child IDs
        child_ids_result = session.exec(select(ChildAnswer.child_id).distinct()).all()

        child_ids = [result for result in child_ids_result]
        stats["total_records"] = len(child_ids)

        # Process each child
        for child_id in child_ids:
            if child_id < 3:
                continue  # skip the 2 pre-existing children including Grogu
            try:
                # Get answer to question 3 (Termingeboren/Fruhgeboren)
                q3_answer = session.exec(
                    select(ChildAnswer)
                    .where(ChildAnswer.child_id == child_id)
                    .where(
                        ChildAnswer.question_id in [3, 25]
                    )  # 3 in original import, 25 in re-import/additional batch
                ).first()

                # Get answer to question 4 (weeks if Fruhgeboren)
                q4_answer = session.exec(
                    select(ChildAnswer)
                    .where(ChildAnswer.child_id == child_id)
                    .where(ChildAnswer.question_id in [4, 26])  # 26 in new import
                ).first()

                # Process based on answers
                if q3_answer and q3_answer.answer == "Termingeboren":
                    # Full term birth (41 weeks)
                    stats["termingeboren_count"] += 1
                    birth_weeks = 41
                    incubator_weeks = 0
                elif q3_answer and q3_answer.answer == "Frühgeboren":
                    # Premature birth
                    stats["fruhgeboren_count"] += 1
                    if q4_answer and q4_answer.answer:
                        birth_weeks, incubator_weeks = parse_weeks(q4_answer.answer)
                        if incubator_weeks > 0:
                            stats["with_incubator_weeks"] += 1
                    else:
                        # Fruhgeboren but no weeks specified
                        birth_weeks = 0  # Unknown
                        incubator_weeks = 0
                        stats["without_birth_info"] += 1
                else:
                    print("Child ID:", child_id)
                    print(
                        "Unknown birth answer!",
                        q3_answer.answer if q3_answer else "None",
                        "Q4 answer [fruhgeboren weeks was:]",
                        q4_answer.answer if q4_answer else "None",
                    )
                    # Unknown birth term
                    birth_weeks = 0  # Unknown
                    incubator_weeks = 0
                    stats["without_birth_info"] += 1

                if not dry_run:
                    # Create or update birth weeks answer
                    existing_birth_answer = session.exec(
                        select(ChildAnswer)
                        .where(ChildAnswer.child_id == child_id)
                        .where(ChildAnswer.question_id == birth_question.id)
                    ).first()

                    if existing_birth_answer:
                        existing_birth_answer.answer = str(birth_weeks)
                    else:
                        birth_answer = ChildAnswer(
                            child_id=child_id,
                            question_id=birth_question.id,
                            answer=str(birth_weeks),
                            additional_answer=None,
                        )
                        session.add(birth_answer)

                    # Create or update incubator weeks answer
                    existing_incubator_answer = session.exec(
                        select(ChildAnswer)
                        .where(ChildAnswer.child_id == child_id)
                        .where(ChildAnswer.question_id == incubator_question.id)
                    ).first()

                    if existing_incubator_answer:
                        existing_incubator_answer.answer = str(incubator_weeks)
                    else:
                        incubator_answer = ChildAnswer(
                            child_id=child_id,
                            question_id=incubator_question.id,
                            answer=str(incubator_weeks),
                            additional_answer=None,
                        )
                        session.add(incubator_answer)

            except Exception as e:
                print(f"Error processing child_id {child_id}: {e}")
                stats["processing_errors"] += 1

        # Commit changes if not dry run
        if not dry_run:
            session.commit()
            print("Changes committed to database")
        else:
            print("[DRY RUN] No changes committed to database")

        # 3. Perform sanity check if not dry run
        if not dry_run:
            total_children = len(child_ids)

            # Count birth answers - using len() on the result list
            birth_answers = session.exec(
                select(ChildAnswer).where(ChildAnswer.question_id == birth_question.id)
            ).all()
            birth_answers_count = len(birth_answers)

            # Count incubator answers - using len() on the result list
            incubator_answers = session.exec(
                select(ChildAnswer).where(
                    ChildAnswer.question_id == incubator_question.id
                )
            ).all()
            incubator_answers_count = len(incubator_answers)

            print("\nSanity check results:")
            print(f"  Total children: {total_children}")
            print(
                f"  Children with birth weeks: {birth_answers_count} ({birth_answers_count / total_children * 100:.1f}%)"
            )
            print(
                f"  Children with incubator weeks: {incubator_answers_count} ({incubator_answers_count / total_children * 100:.1f}%)"
            )

            if birth_answers_count < 0.9 * total_children:
                print("\nWARNING: Less than 90% of children have birth week answers!")

        # Print statistics
        print("\nProcessing statistics:")
        print(f"  Total children processed: {stats['total_records']}")
        print(f"  Full-term births (Termingeboren): {stats['termingeboren_count']}")
        print(f"  Premature births (Fruhgeboren): {stats['fruhgeboren_count']}")
        print(f"  With incubator weeks specified: {stats['with_incubator_weeks']}")
        print(f"  Without birth information: {stats['without_birth_info']}")
        print(f"  Processing errors: {stats['processing_errors']}")

        print("\nDone!")
