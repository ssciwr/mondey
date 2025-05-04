from mondey_backend.import_data.postprocessing_corrections.correct_ja_nein_question_answer_options import (
    correct_ja_nein_question_answer_options,
)
from mondey_backend.import_data.postprocessing_corrections.remove_answer_text_encoding import (
    remove_encoding_in_text_answers,
)
from mondey_backend.import_data.postprocessing_corrections.update_started_value_for_answersessions import (
    update_started_value_for_answersessions,
)
from mondey_backend.import_data.utils import data_path


# cleanup_question is really functioning as "are you running this for the first time", this function needs
# to be refactored into the two main versions of it really, and the question deletion/merging stuff should only
# happen when you run it for the first time.
def run_postprocessing_corrections(
    relevant_data_csv_path, dry_run=True, cleanup_questions=False
):
    # Improve raw data
    print("Improving raw data.")
    remove_encoding_in_text_answers()  # still need, works on additional, does not affect existing
    print("Removed encoding.")
    correct_ja_nein_question_answer_options()  # still need, works on additional, does not affect existing
    print("Correct yes/no answers.")
    update_started_value_for_answersessions(
        relevant_data_csv_path
    )  # still need, works on additional, does not affect existing
    print("Cleaned up raw data.")


# For testing..
if __name__ == "__main__":
    run_postprocessing_corrections(data_path, dry_run=True)
