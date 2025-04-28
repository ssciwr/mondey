from mondey_backend.import_data.postprocessing_corrections.convert_fruhgeboren_data_into_two_questions import (
    transform_birth_terms,
)
from mondey_backend.import_data.postprocessing_corrections.correct_ja_nein_question_answer_options import (
    correct_ja_nein_question_answer_options,
)
from mondey_backend.import_data.postprocessing_corrections.delete_children_age_survey_answers import (
    delete_children_age_survey_answers,
)
from mondey_backend.import_data.postprocessing_corrections.delete_previous_birth_terms_questions import (
    delete_previous_birth_terms_questions,
)
from mondey_backend.import_data.postprocessing_corrections.merge_eltern_question_and_answers import (
    merge_eltern_question,
)
from mondey_backend.import_data.postprocessing_corrections.remove_answer_text_encoding import (
    remove_encoding_in_text_answers,
)
from mondey_backend.import_data.postprocessing_corrections.transform_younger_older_siblings import (
    transform_younger_older_siblings,
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
    remove_encoding_in_text_answers()
    print("Removed encoding.")
    correct_ja_nein_question_answer_options()
    print("Correct yes/no answers.")
    update_started_value_for_answersessions(relevant_data_csv_path)
    print("Cleaned up raw data.")

    # Transform answers to be more useful
    print("Transforming answers.")
    if cleanup_questions:
        transform_younger_older_siblings()
        merge_eltern_question()  # so the problem is, the old data will already be merged. But the new rows won't be merged.
    else:
        pass
        # todo: Partial version of transform_younger_older_siblings only for the new children
        # update_user_answers(new_id, old_ids) # from merge_eltern_question
    # because of the approach of deleting the processed questions
    print("Deleting children age survey answers...")
    delete_children_age_survey_answers()
    print("Transforming the birth terms question & answers...")
    transform_birth_terms(dry_run=dry_run)
    # todo: Need to make transforming birth terms actually work.
    # not needed as already done after initial import:
    if cleanup_questions:
        delete_previous_birth_terms_questions(dry_run=dry_run)
    # no translation of questions needed as we are re-using the english questions (which have german and english texts)
    print("All postprocessing complete.")


# For testing..
if __name__ == "__main__":
    run_postprocessing_corrections(data_path, dry_run=True)
