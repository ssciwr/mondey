"""
We deal in a hardcoded way with answers to questions which our import script significantly changed/merged.
We basically assign the answer either to the correct question ID or additional answer property as relevant,
or for birth year questions/answers, skip.

- Children Birth age (FK01 FK02) - don't save, skip.
- Fruhgeboren / Termingeboren: parse it automatically upon saving, save direct into question IDs.
- Eltern questions (this includes: ) - just save to the Eltern question instead.

We also need a test.

"""

# We match by the question name. This is because, we needed to show a readable, understandable name in the frontend.
# Before, using e.g. the variable like "FP01, FK04" made little sense so we stored the name, but not the variable.
# However, in the latest form data, these changed a bit (the meta_changed_questions), and because we did some operations
# on the original data to make it work with multi level questions, we need to make those same questions again now.

age_of_birth_questions = ["Geburtsjahr", "Geburtsmonat"]
eltern_questions = ["Mütter", "Väter", "Eltern", "Andere Verwandte"]
fruhgeboren_questions = ["Fruhgeboren? [01]", "Termingeboren"]
younger_older_sibling_questions = ["Jüngere Geschwister", "Ältere Geschwister"]
meta_changed_questions = {  # this maps the "new/latest" version in the data to the old/original question "name" tag.
    "Fremdbetreuung?": "Fremdbetreuung"
}

meta_only_changed_questions = list(meta_changed_questions.keys())


def is_special_answer_case(question_label):
    return question_label in [
        *eltern_questions,
        *fruhgeboren_questions,
        *age_of_birth_questions,
        *younger_older_sibling_questions,
    ]


def process_special_answer(question_label, answer, is_parent_question=False):
    if is_parent_question and (question_label in age_of_birth_questions):
        print("Age of birth case - skip, no need to save anything.")
        return
    if question_label in eltern_questions:
        # todo
        # if this answer is true, we should save it to the eltern question, which has the ID of:
        eltern_question_special_id = 13
        print(eltern_question_special_id)
    elif (
        question_label in fruhgeboren_questions
        or question_label in younger_older_sibling_questions
    ):
        # todo
        pass
        # in this case, for child questions with IDs 17 and 18 (older/yougner siblings), basically I think the
        # additional data sometimes has no value, so this would simply set the answer to be "0". It doesn't need to
        # change the question type. But also, if the answer is not 0, it should save the real answer too.


# todo: this needs to import the saving answer stuff at least.

"""
Rough changed answer processing code:

If question is_hardcoded_type:
process_special_answer

else: lookup the question.

else (if not found) throw error because we have not accounted for the question so it's probably a special one that
still needs to be there.
"""
