from mondey_backend.import_data.import_childrens_question_answers_data import (
    import_childrens_question_answers_data,
)
from mondey_backend.import_data.utils import data_path
from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.import_data.utils import labels_path
from mondey_backend.import_data.utils import questions_configured_path

"""
Once the files in utils have been put in this directory, this file imports all data from start to finish.

You will usually want to clear the (import-specific) database each time you run this. To do that, run
`python3 -m import_all.py true`. This will wipe whatever is in the import_data/db databases in terms of data.
"""

if __name__ == "__main__":
    import_current_session, import_current_engine = get_import_current_session()

    # import_milestones_metadata(import_current_session, milestones_metadata_path)

    print("Now assigning children their milestones")
    # map_children_milestones_data(data_path, import_current_session)
    print("Done assigning children their milestones.")

    print("Now setting the custom question/answers pairs")
    import_childrens_question_answers_data(
        import_current_session,
        labels_path,
        data_path,
        questions_configured_path,
        clear_existing_questions_and_answers=False,
    )
