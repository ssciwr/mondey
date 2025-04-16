import pandas as pd
from mmondey_backend.import_data.utils import labels_path

from mondey_backend.import_data.import_children_with_assigned_milestone_data import (
    map_children_milestones_data,
)
from mondey_backend.import_data.import_childrens_question_answers_data import (
    assign_answers_to_the_imported_questions,
)
from mondey_backend.import_data.postprocessing_corrections.run_postprocess_corrections import (
    run_postprocessing_corrections,
)
from mondey_backend.import_data.utils import additional_data_path
from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.import_data.utils import questions_configured_path


def align_additional_data_to_current_answers():
    """
    This function assumes that you have placed the additional data in the additional data file paths,and that the mondey.db and user.db
    file in /import_data are the ones you want to build the data on top of. So it skips importing/aligning
    the milestone meta IDs.

    The script does not support updating or changing answers for existing children.
    It only supports adding data with new children.

    It first inserts any children (and corresponding parents as users), ignoring duplicates.
    Then it inserts the milestone answers for those children (same map_children_milestones_data function).

    Then it inserts the question answers for those children/answers.

    Then it runs the postprocessing_corrections/run_postprocess_corrections.py script.

    :return:
    """

    # Check we have all additional data files:
    labels_df = pd.read_csv(
        labels_path,
        sep=",",
        encoding="utf-16",
        encoding_errors="replace",
        index_col=None,
    )
    additional_data_df = pd.read_csv(
        additional_data_path, sep="\t", encoding="utf-16", encoding_errors="replace"
    )
    questions_configured_df = pd.read_csv(
        questions_configured_path,
        sep=",",
        encoding="utf-8",
        dtype=str,
        encoding_errors="replace",
    )

    import_current_session, import_current_engine = get_import_current_session()

    print("Now assigning the additional children their milestones")
    map_children_milestones_data(
        additional_data_path, import_current_session
    )  # already deals with existing children.

    # Only answers - do not re-add the questions
    assign_answers_to_the_imported_questions(
        import_current_session, additional_data_df, labels_df, questions_configured_df
    )

    run_postprocessing_corrections(dry_run=False)

    print(
        "Finished! All additional data added. Remember to re-run and update the stats if you want to see the updated"
        "research data from these additional sessions in the UI - the scores will only calculate when the stats update"
        "gets ran (e.g. by running async_update_stats or using the endpoint for update-stats/{incremental_update})"
    )
