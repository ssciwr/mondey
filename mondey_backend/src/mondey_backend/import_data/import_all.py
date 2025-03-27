from mondey_backend.databases.mondey import create_mondey_db_and_tables
from mondey_backend.import_data.import_children_with_assigned_milestone_data import (
    map_children_milestones_data,
)
from mondey_backend.import_data.import_childrens_question_answers_data import (
    import_childrens_question_answers_data,
)
from mondey_backend.import_data.import_milestones_metadata import (
    import_milestones_metadata,
)
from mondey_backend.import_data.utils import data_path
from mondey_backend.import_data.utils import get_import_test_session
from mondey_backend.import_data.utils import labels_path
from mondey_backend.import_data.utils import milestones_metadata_path
from mondey_backend.import_data.utils import questions_configured_path

if __name__ == "__main__":
    import sys

    clear_existing = sys.argv[1]

    if clear_existing and (
        input(
            "This will wipe your DB data! Are you certain you want to *delete all data*? (y/n)"
        )
        != "y"
    ):
        exit()

    import_session, import_engine = get_import_test_session()
    create_mondey_db_and_tables(optional_engine=import_engine)

    import_milestones_metadata(
        import_session,
        milestones_metadata_path,
        clear_existing_milestones=clear_existing,
    )
    print("Now assigning children their milestones")
    map_children_milestones_data()
    print("Now setting the custom question/answers pairs")
    import_childrens_question_answers_data(
        import_session,
        labels_path,
        data_path,
        questions_configured_path,
        clear_existing_questions_and_answers=False,
    )

"""

Remaining major todos on data import:
Check whether these should be discarded or not?
Discarding question answer without found saved question (which was deliberately not saved, maybe because it was a milestone etc):  FK05 Gesundheit: Ausweichoption (negativ) oder Anzahl ausgewählter Optionen
Discarding question answer without found saved question (which was deliberately not saved, maybe because it was a milestone etc):  FK05_01 Gesundheit: Motorik
Discarding question answer without found saved question (which was deliberately not saved, maybe because it was a milestone etc):  FK05_02 Gesundheit: Denken
Discarding question answer without found saved question (which was deliberately not saved, maybe because it was a milestone etc):  FK05_03 Gesundheit: Sprache

"""
