"""
We deal in a hardcoded way with answers to questions which our import script significantly changed/merged.
We basically assign the answer either to the correct question ID or additional answer property as relevant,
or for birth year questions/answers, skip.

- Children Birth age (FK01 FK02) - don't save, skip.
- Fruhgeboren / Termingeboren: parse it automatically upon saving, save direct into question IDs.
- Eltern questions (this includes: ) - just save to the Eltern question instead.

We also need a test.

"""

from mondey_backend.import_data.postprocessing_corrections.convert_fruhgeboren_data_into_two_questions import (
    parse_weeks,
)
from mondey_backend.import_data.utils import get_childs_parent_id
from mondey_backend.import_data.utils import update_or_create_user_answer

# We match by the question name. This is because, we needed to show a readable, understandable name in the frontend.
# Before, using e.g. the variable like "FP01, FK04" made little sense so we stored the name, but not the variable.
# However, in the latest form data, these changed a bit (the meta_changed_questions), and because we did some operations
# on the original data to make it work with multi level questions, we need to make those same questions again now.

age_of_birth_questions = ["Geburtsjahr", "Geburtsmonat"]
eltern_questions = ["Mütter", "Väter", "Eltern", "Andere Verwandte"]
specific_fruhgeboren_week_questions = ["Fruhgeboren [01]", "Fruhgeboren? [01]"]
fruhgeboren_questions = [*specific_fruhgeboren_week_questions, "Termingeboren"]
younger_older_sibling_questions = ["Jüngere Geschwister", "Ältere Geschwister"]
meta_changed_questions = {  # this maps the "new/latest" version in the data to the old/original question "name" tag.
    "Fremdbetreuung?": "Fremdbetreuung"
}
andere_diagnosed_question = "Andere Diagnosen: [01]"

child_age_questions_labels = ["FK01", "FK02"]

meta_only_changed_questions = list(meta_changed_questions.keys())

"""
Match based on question text ("Name" attribute). We save as "name" so that researchers can have something
useable to select the questions with on the research page, but the name can change between form data versions.
That's why we hardcode to rematch old data. Since we also need to manage merging/flattening some questions,
it's not a major difference matching by name (We could also match by variable code, which we do in one
special case below, but storing that as a DB field doesn't add much given we need to do flattening anyway)
"""


def is_special_answer_case(question_label: str, variable: str) -> bool:
    # excepts for labels which are the same for parents and children
    if variable in child_age_questions_labels:
        return False  # special case because parent also has "Geburtsjahr", but that one, we keep.
    return question_label in [
        *eltern_questions,
        *fruhgeboren_questions,
        *age_of_birth_questions,
        *younger_older_sibling_questions,
    ]


def process_special_answer(
    session, question_label: str, answer: str, variable: str, child_id: int
):
    if variable in child_age_questions_labels:
        print("Age of birth case - skip, no need to save anything.")
        return
    elif question_label in eltern_questions:
        eltern_question_special_id = 13
        print(eltern_question_special_id)
        if answer is not None and len(answer) > 0:
            # save parent answer for this question, only if it was actually filled out.
            # Check what we did the first time. Did we save direct or as additional answer?
            update_or_create_user_answer(
                session,
                user_or_child_id=get_childs_parent_id(session, child_id),
                question_id=eltern_question_special_id,
                answer_text=answer,
                set_only_additional_answer=False,  # question_label == "Andere Verwandte" would not be correct
                # - that's just a category, not a way for users to specify in freetext
                is_child_question=False,
            )
    elif question_label in fruhgeboren_questions:
        # Termingeboren/Fruhgeboren = 3
        # Fruhgeboren [01] = 4 (Weeks only if the former is "Fruhgeboren")
        pregnancy_duration_question_id = 21
        incubator_weeks_question_id = 22
        pregnanacy_duration_answer = 41  # 41 weeks assumed if Termingeboren
        incubator_weeks = 0
        if (
            question_label in specific_fruhgeboren_week_questions
        ):  # Fruhgeboren specific weeks part.
            if answer is not None and len(answer):  # parse it as before...
                pregnanacy_duration_answer, incubator_weeks = parse_weeks(answer)
            # This ignores the users choice for Termingeboren/Fruhgeboren - if any duration period is specified, it assumes
            # we should record and overwrite the info (which makes sense based on the data)

        update_or_create_user_answer(
            session,
            user_or_child_id=child_id,
            question_id=pregnancy_duration_question_id,
            answer_text=str(pregnanacy_duration_answer),
            set_only_additional_answer=False,
            is_child_question=False,
        )
        update_or_create_user_answer(
            session,
            user_or_child_id=child_id,
            question_id=incubator_weeks_question_id,
            answer_text=str(incubator_weeks),
            set_only_additional_answer=False,
            is_child_question=False,
        )
    elif question_label in younger_older_sibling_questions:
        """
        Relevant questions as in the data:
          FK08 Geschwister?: Ausweichoption (negativ) oder Anzahl ausgewählter Optionen
            FK08_01: Geschwister?: Ja, ältere Geschwister

            FK08_02: Geschwister?: Ja, jüngere Geschwister

            FK08_03: Geschwister?: Nein, keine weiteren Geschwister, die mit im Haushalt leben

        """
        relevant_question_id = 17 if question_label == "Jüngere Geschwister" else 18
        update_or_create_user_answer(
            session,
            user_or_child_id=child_id,
            question_id=relevant_question_id,
            answer_text=answer
            if answer is not None and len(str(answer)) > 0
            else "0",  # set to 0 by default for numerical scales
            set_only_additional_answer=False,
            is_child_question=True,
        )
    elif question_label == andere_diagnosed_question:
        print("Andere case.. label was: ", question_label, ", and  answer:", answer)
        # if it is the normal Andere Diagnosen question with Ja/Nein, it will just be saved normally.
        # What we are doing is writing in the answer to question 12 (the freetext form) when it is selected,
        # rather than save to question 12.
        andere_diagnosen_question_id = 10
        # fix... rerun fresh with  is_Child_question=False now...
        update_or_create_user_answer(
            session,
            user_or_child_id=child_id,
            question_id=andere_diagnosen_question_id,
            answer_text=answer,  # set to 0 by default for numerical scales
            set_only_additional_answer=True,
            is_child_question=False,
        )


"""
Remaining todos:
Get the titles for andere diagnosen in the new data import.

Important: Do younger/older siblings import right.

=> Get the actual response of the child...
response_label = labels_df[
                    (labels_df["Variable"] == variable)
                    & (labels_df["Response Code"] == response)
                ]

"""
