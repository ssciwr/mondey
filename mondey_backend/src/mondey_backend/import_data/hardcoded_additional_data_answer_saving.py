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
eltern_question_variables = ["FP01", "FP02", "FP03", "FP04"]
specific_fruhgeboren_week_questions = ["Fruhgeboren [01]", "Fruhgeboren? [01]"]
fruhbgeboren_and_teringeboren_variables = ["FK03", "FK04_01"]
fruhgeboren_questions = [*specific_fruhgeboren_week_questions, "Termingeboren"]
younger_older_sibling_questions = ["Jüngere Geschwister", "Ältere Geschwister"]
younger_older_sibling_variables = [
    "FK08_01",
    "FK08_02",
]  # other ones just contain info these have within them?


andere_diagnosed_question = "Andere Diagnosen: [01]"

child_age_questions_labels = ["FK01", "FK02"]
variables_to_ignore_with_reasons = {
    "FK08": "Needless younger sibling related yes/no question",
    "FK08_03": "Needless younger sibling related question",
}

gesundheit_variables = [
    "FK05_01",
    "FK05_02",
    "FK05_03",
    "FK05_04",
    "FK05_05",
    "FK05_06",
    "FK05_07",
    "FK06_01",
]
# FK06_01 = Andere Diagnosen..
andere_diagnosen_other_question_variable = "FK06_01"
nationality_other_question_variable = "FE03_01"  #' Andere Staatsangehörigkeit: [01]
muttersprache_other_question_variable = "FE05_01"
additional_answer_variables = [
    andere_diagnosen_other_question_variable,
    nationality_other_question_variable,
    muttersprache_other_question_variable,
]


relevant_child_variables = [
    *fruhbgeboren_and_teringeboren_variables,
    *gesundheit_variables,
    andere_diagnosen_other_question_variable,
    "FK07",
    "FK11",
    "FK12",
    *younger_older_sibling_variables,
]
relevant_user_variables = [
    *eltern_question_variables,
    "FE08",
    "FE07",
    "FE06",
    "FE04",
    muttersprache_other_question_variable,
    nationality_other_question_variable,
]

hardcoded_id_map = {
    # Numeric IDs mapped to variable names
    "FK05_01": 5,
    "FK05_02": 6,
    "FK05_03": 7,
    "FK05_04": 8,
    "FK05_05": 9,
    "FK05_06": 10,  # With additional answer "Andere Diagnosen: [01]"
    "FK05_07": 11,
    "FK07": 13,
    "FK08_01": "FK09",  # Count older siblings or null if 0
    "FK08_02": "FK10",  # Count younger siblings
    "FK11": 19,
    "FK12": 20,
    "FK03": 3,  # Related to questions 21 & 22
    "FK04_01": 4,  # Related to questions 21 & 22
    # we just save answers to the non-existing 3 and 4 question and let the tested working script convert that
    # to update the asnwers to point to 21/22 for Termingeboren.
    # User Questions mapped to numeric IDs
    "FP01": 13,  # Eltern giant question
    "FP02": 13,  # Eltern giant question
    "FP03": 13,  # Eltern giant question
    "FP04": 13,  # The "andere" option # in this case, only one of these will have a non-null, non empty value,
    # so we just write it.
    "FE08": 7,
    "FE07": 6,
    "FE06": 5,
    "FE04": 4,  # Muttersprache
    "FE05_01": 4,  # Muttersprache (andere option)
    "FE02": 3,  # Nationalität
    "FE03_01": 3,  # Nationalität (andere option)
}
all_relevant_variables = [*relevant_user_variables, *relevant_child_variables]

hardcoded_other_answers = {
    andere_diagnosen_other_question_variable: 10,
    nationality_other_question_variable: 4,
    muttersprache_other_question_variable: 3,
}

"""
Hardcoded matching based on specific variable ID for the non-milestone relevant answers we want to store and process
into the database. Process meaning, for some questions, like the Eltern one, we convert several individual
questions on the same theme into the """


def should_be_saved(variable: str) -> bool:
    return variable in all_relevant_variables  # otherwise it is a milestone


def process_special_answer(
    session, question_label: str, answer: str, variable: str, child_id: int
):
    print(
        "Deactivated. JUst save through normal process with an allowlist of approved variable IDs and variable matching now"
    )
    return
    if variable in child_age_questions_labels:
        print("Age of birth case - skip, no need to save anything.")
        return
    elif variable in eltern_question_variables:
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
    elif variable in fruhbgeboren_and_teringeboren_variables:
        # Termingeboren/Fruhgeboren = 3
        # Fruhgeboren [01] = 4 (Weeks only if the former is "Fruhgeboren")
        pregnancy_duration_question_id = 21
        incubator_weeks_question_id = 22
        pregnanacy_duration_answer = 41  # 41 weeks assumed if Termingeboren
        incubator_weeks = 0
        # first bit is Fruhgeboren specific weeks part.
        if (
            variable == "FK04_01" and answer is not None and len(answer)
        ):  # parse it as before...
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
    elif variable in younger_older_sibling_variables:
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
