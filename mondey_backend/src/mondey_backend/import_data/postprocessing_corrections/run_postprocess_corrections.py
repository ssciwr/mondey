from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.convert_fruhgeboren_data_into_two_questions import (
    transform_birth_terms,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.correct_ja_nein_question_answer_options import (
    correct_ja_nein_question_answer_options,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.delete_previous_birth_terms_questions import (
    delete_previous_birth_terms_questions,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.merge_eltern_question_and_answers import (
    merge_eltern_question,
)
from mondey_backend.src.mondey_backend.import_data.postprocessing_corrections.remove_answer_text_encoding import (
    remove_encoding_in_text_answers,
)


def run_postprocessing_corrections(dry_run=True):
    remove_encoding_in_text_answers()
    merge_eltern_question()
    transform_birth_terms(dry_run=dry_run)
    delete_previous_birth_terms_questions(dry_run=dry_run)
    correct_ja_nein_question_answer_options()
