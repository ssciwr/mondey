from mondey_backend.import_data.postprocessing_corrections.convert_fruhgeboren_data_into_two_questions import (
    transform_birth_terms,
)
from mondey_backend.import_data.postprocessing_corrections.correct_ja_nein_question_answer_options import (
    correct_ja_nein_question_answer_options,
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
from mondey_backend.import_data.utils import data_path
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.delete_children_age_survey_answers import (
    delete_children_age_survey_answers,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.transform_younger_older_siblings import (
    transform_younger_older_siblings,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.update_started_value_for_answersessions import (
    update_started_value_for_answersessions,
)


def run_postprocessing_corrections(relevant_data_csv_path, dry_run=True):
    # Improve raw data
    remove_encoding_in_text_answers()
    correct_ja_nein_question_answer_options()
    update_started_value_for_answersessions(relevant_data_csv_path)

    # Transform question types to be more useful
    transform_younger_older_siblings()
    delete_children_age_survey_answers()
    merge_eltern_question()
    transform_birth_terms(dry_run=dry_run)
    delete_previous_birth_terms_questions(dry_run=dry_run)
    # no translation of questions needed as we are re-using the english questions (which have german and english texts)


# For testing..
if __name__ == "__main__":
    run_postprocessing_corrections(data_path, dry_run=True)
