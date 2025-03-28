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

"""
Once the files in utils have been put in this directory, this file imports all data from start to finish.

You will usually want to clear the (import-specific) database each time you run this. To do that, run
`python3 -m import_all.py true`. This will wipe whatever is in the import_data/db databases in terms of data.
"""

if __name__ == "__main__":
    import sys

    clear_existing = sys.argv[1] if len(sys.argv) > 1 else False

    if (
        clear_existing
        and (
            input(
                "This will wipe your DB data! Are you certain you want to *delete all data*? (y/n)"
            )
            != "y"
        )
        or not clear_existing
        and (
            input(
                "You are running this without wiping the import data first, so duplicate data might be saved. Do you "
                "really want to run this on top of existing data, without clearing any existing import_data/db data? Run "
                "with `import_data.py true` to wipe existing data."
            )
            != "y"
        )
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
    map_children_milestones_data(data_path, import_session)
    print("Done assigning children their milestones.")

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
