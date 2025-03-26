"""
This file should parse each column and if it is a childs question, save it.
Select options will (as in `ChildQuestion` class/SQL model) just be saved as plaintext answers.

Care must be taken for freetext options. Those seem to be generally indicated by a "_" or "_01" affix to the question,
e.g.:

FE03 <-- will be a code-mapped answer
FE03_01 <-- optional freetext answer (when present, overwrites the code-mapped answer)

They are also easy to tell apart because the "Type" will be "TEXT" not "ORDINAL". e.g.

FE01 <-- ORDINAL (e.g. 1, 2, 3, 4, 5, 6, 7 -9) (where these are mapped to 1 = Deutschland, 2 = Sweden, usw).
FE01_031 <-- TEXT (e.g. "Frankreich")

Notes:

    We use variable + ': ' + variable_label for the question ID (so "FE06: Geburtsjahr") because there are some
    complexities in the question mapping from the SoSci data, especially:
    1) For answers, each possibly mappable answer response duplicates the question...
    e.g.
    Variable | Name | Code | Label
    FE04 Geburtsjahr 1 2024
    FE04 Geburtsjahr 2 2023
    FE04 Geburtsjahr 3 2022

    ... But more than this...

    The same question might appear again (e.g. in reference to the Parent/Beobachter, not the child):
    Variable | Name | Code | Label
    FK04 Geburtsjahr 1 1972
    FK04 Geburtsjahr 2 1973
    FK04 Geburtsjahr 3 1974

    So the *same Name*, *same Codes*, but Different Labels if the "Variable" (really "variable ID") is the same.
    Since variable ID also gets duplicated nAnswers times, the logic keeps within our system the variable tag
    alongside the label at all times. This way we can be sure we actually have got the respective FE04 vs FK04
    Geburtsjahr question/answers data, to avoid confusing those two. This way is also more dynamic. No combinations
    (because of how SoSci exports) should ever have the same variable and name unless they are mapping the same set
    of answers, like our code processed them. Yes it does mean in the UI the "Variable"(string ID) will appear as a
    prefix, but that's a great traddeoff to have certainty in the variables being in the actual data.
"""

import json

import pandas as pd
from sqlmodel import select

from mondey_backend.import_data.utils import clear_all_data
from mondey_backend.import_data.utils import data_path
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.import_data.utils import labels_path
from mondey_backend.models.milestones import Language
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText

# todo: Eventually this needs to parse Igor filled-out questions.csv file in order to also set the "required"
# - also do the requried migration when doing that...
# property for questions, and to save as a "question about the  beobachter" if such a question (like Birth Year
# of the carer / parent). I think those questions may be saved under users questions, in which case we may need to
# generate users for each child to store those answers, with no research, non admin settings.

debug = True

satisfyPreCommitUnusedImportRemover = type(Language) is str


def import_childrens_question_answers_data(
    session,
    labels_path: str,
    data_path: str,
    clear_existing_questions_and_answers: bool = False,
) -> list[tuple[str, str]]:
    if debug:
        print("Opening labels path: ", labels_path)
        print("Opening data path: ", data_path)
    if satisfyPreCommitUnusedImportRemover:
        print("Satisfied pre-commit so we can have language model table access...")

    labels_df = pd.read_csv(labels_path, sep=",", encoding="utf-16")
    data_df = pd.read_csv(data_path, sep="\t", encoding="utf-16")

    if clear_existing_questions_and_answers:
        clear_all_data(session)

    free_text_questions = []

    # Dictionary to track the previous variable for handling 'Andere' cases
    previous_variable = None
    # previous_variable_label = None

    # Process each unique variable in labels_df
    processed_variables = set()
    if debug:
        print("Sample data:")
        print(labels_df.head(5))

    for _uj, label_row in (
        labels_df.groupby("Variable").first().reset_index().iterrows()
    ):
        variable = label_row["Variable"]
        if debug:
            print(label_row)
            print("has variable: ", variable)

        # Skip if already processed
        if variable in processed_variables:
            continue
        processed_variables.add(variable)

        # Determine question type and properties
        variable_type = label_row["Variable Type"]
        input_type = label_row["Input Type"]
        variable_label = label_row["Variable Label"]

        # Handling different variable types
        if (
            variable_type == "NOMINAL" or variable_type == "ORDINAL"
        ) and input_type == "MC":
            if debug:
                print(
                    "Handling Multiple Choice with optinos.. should be saved as separated text strings"
                )
            # Multiple Choice Question
            options = labels_df[labels_df["Variable"] == variable]
            if debug:
                print("Options found were: ", options)

            # Filter out non-response codes
            valid_options = options[options["Response Code"] != -9]

            # Prepare options JSON
            options_dict = {
                str(row["Response Code"]): row["Response Label"]
                for _, row in valid_options.iterrows()
            }
            if debug:
                print("Sample options: ", options_dict)

            # Create ChildQuestion
            child_question = ChildQuestion(
                component="select",
                type="text",
                required=False,
                text={
                    "de": ChildQuestionText(
                        question=variable + ": " + variable_label,
                        options_json=json.dumps(options_dict),
                        options=", ".join(options_dict.values()),
                        lang_id=1,  # hardocded: This is the first language, which is German by default, amtching the questions
                    )
                },
            )
            session.add(child_question)

            # Track this as the previous variable for potential 'Andere' handling
            previous_variable = variable
            # previous_variable_label = variable_label

        elif variable_type == "TEXT" and input_type == "TXT":
            # These are free text questions
            if (
                type(variable) is str
                and "[01]" in variable
                and (previous_variable and f"{previous_variable}_01" in variable)
            ):  # only if they match
                # = it's an other free text input, we handle in geenral data processing rules for TEXT variable type later.
                continue

            # Independent free text question
            free_text_questions.append((variable, variable_label))

            child_question = ChildQuestion(
                component="text",
                type="text",
                required=False,
                text={
                    "de": ChildQuestionText(
                        question=variable + ": " + variable_label, lang_id=1
                    )
                },
            )
            session.add(child_question)
            if debug:
                print("Added text feetex tquestion type..")
        else:
            if debug:
                print(
                    "Question case was not hanlded... need to pay attention to this..",
                    variable_label,
                    variable_type,
                    input_type,
                )

        # For other less common types, skip or handle as needed
    session.commit()
    questions_to_discard = []
    total_answers = 0
    missing = 0

    # Process actual data into child answers
    for _, child_row in data_df.iterrows():
        # Iterate through all variables in labels_df
        for _j, label_row in (
            labels_df.groupby("Variable").first().reset_index().iterrows()
        ):
            variable_type = label_row["Variable Type"]
            variable = label_row["Variable"]
            variable_label = label_row["Variable Label"]

            if variable_label in questions_to_discard:
                continue

            # Find the corresponding ChildQuestion
            query = (
                select(ChildQuestion)
                .join(ChildQuestionText)
                .where(
                    ChildQuestionText.lang_id == 1,
                    ChildQuestionText.question == variable + ": " + variable_label,
                )
            )

            child_question = session.exec(query).first()  # why doesn't this work?

            if not child_question:
                if debug:
                    print("No child question...")
                    print(label_row["Variable Label"])
                continue
            else:
                questions_to_discard.append(variable)

            # Get the child's response for this variable
            response = child_row.get(variable)

            # Skip if no response
            if pd.isna(response) or response == -9:
                continue

            # Handle Multiple Choice
            if variable_type == "NOMINAL" or variable_type == "ORDINAL":
                if debug:
                    print("Came across nominal...")
                response_label = labels_df[
                    (labels_df["Variable"] == variable)
                    & (labels_df["Response Code"] == response)
                ]  # todo: Fix - empty dataframe.
                if debug:
                    print(
                        "Response/Response label: ", response, "../..", response_label
                    )
                    print("ANd desired variable: ", variable)

                if not response_label.empty:
                    answer_text = response_label.iloc[0]["Response Label"]
                    if debug:
                        print(
                            "Answer leg assigned for response code: ",
                            response,
                            " was: ",
                            answer_text,
                        )

                    # Special handling for 'Andere' cases which are usually but not always free text
                    if answer_text == "Andere" or answer_text == "Other":
                        if debug:
                            print("Free text Andere triggered!")
                        # Look for free text input
                        free_text_var = f"{variable}_01"
                        free_text_answer = child_row.get(free_text_var)

                        if not pd.isna(free_text_answer):
                            answer_text = str(free_text_answer)

                    child_answer = ChildAnswer(
                        child_id=child_row["CASE"],
                        question_id=child_question.id,
                        answer=answer_text,
                    )
                    total_answers += 1
                    session.add(child_answer)

            elif variable_type == "TEXT":
                child_answer = ChildAnswer(
                    child_id=child_row["CASE"],
                    question_id=child_question.id,
                    answer=str(response),
                )
                # not sure this will work for free text other cases.
                total_answers += 1
                session.add(child_answer)
            else:
                print("Variable type has no clear processing method! Warning.")
                print(
                    variable_type,
                    "... it has the variable type/label:",
                    variable_type,
                    variable_label,
                )
                missing += 1

    session.commit()
    print("Total answers saved: ", total_answers)
    print(
        "Missing (unable to deal with answers, to which we saved the questions, so wanted the answers): ",
        missing,
    )

    return free_text_questions


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 1 or len(sys.argv) > 2:
        print(
            "Usage: python import_childrens_question_answers_data.py <?clear_existing_questions bool>"
        )
        sys.exit(1)

    clear_existing_questions_and_answers = False
    if len(sys.argv) > 1:
        clear_existing_questions_and_answers = sys.argv[1] == "true"

    if clear_existing_questions_and_answers and (
        input(
            "This will wipe your DB data on questions/answers! Are you certain you want to *delete all such data*? (y/n)"
        )
        != "y"
    ):
        exit()

    import_session, import_engine = get_import_test_session()

    import_childrens_question_answers_data(
        import_session,
        labels_path,
        data_path,
        clear_existing_questions_and_answers=clear_existing_questions_and_answers,
    )
