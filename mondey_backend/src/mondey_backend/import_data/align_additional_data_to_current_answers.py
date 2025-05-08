import asyncio

import pandas as pd

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
from mondey_backend.import_data.utils import labels_path
from mondey_backend.import_data.utils import questions_configured_path


async def align_additional_data_to_current_answers(
    data_path: str = additional_data_path,
    labelling_path: str = labels_path,
    questions_configuration_path: str = questions_configured_path,
):
    """
    This function assumes that you have placed the additional data in the additional data file paths,and that the mondey.db and user.db
    file in /import_data are the ones you want to build the data on top of. So it skips importing/aligning
    the milestone meta IDs.

    Note that given the actual additional data is simply overlaid, we match by child ID and do not add duplicate data
    where it already exists for the childrens milestone or question answers.

    The script does not support updating or changing answers for existing children.
    It only supports adding data with new children.

    It first inserts any children (and corresponding parents as users), ignoring duplicates.
    Then it inserts the milestone answers for those children (same map_children_milestones_data function).

    Then it inserts the question answers for those children/answers.

    Then it runs the postprocessing_corrections/run_postprocess_corrections.py script.

    The challenge with the additional data containing data that already exists and writing on an existing DB is
    that our postprocessing of questions has to work correctly (e.g. mapping the multi part questions)

    :return:
    """
    # Check we have all additional data files:
    labels_df = pd.read_csv(
        labelling_path,
        sep=",",
        encoding="utf-16",
        encoding_errors="replace",
        index_col=None,
    )
    additional_data_df = pd.read_csv(
        data_path, sep="\t", encoding="utf-16", encoding_errors="replace"
    )
    questions_configured_df = pd.read_csv(
        questions_configuration_path,
        sep=",",
        encoding="utf-8",
        dtype=str,
        encoding_errors="replace",
    )

    import_current_session, import_current_engine = get_import_current_session()

    # First, remove duplicates - determined by detecting if there is a child with a name for this import
    # CASE ID and a parent with the user id too with the childs case ID in their email.
    # Remove them from the CSV if so.
    # this way everything downstream like generating parents for children etc will avoid duplicate data.
    # since we don't path the dataframe to these functions, we edit the CSV itself. This also lets us inspect
    # and see which rows the CSV detected as novel/new rows and which it removed as duplicates.

    print("Now assigning the additional children their milestones")
    print("Additional data CSV:", data_path)
    await map_children_milestones_data(
        data_path, import_current_session
    )  # already deals with existing children.

    # Only answers - do not re-add the questions
    assign_answers_to_the_imported_questions(
        import_current_session,
        additional_data_df,
        labels_df,
        questions_configured_df,
        appending_additional_data=True,
    )

    run_postprocessing_corrections(data_path, dry_run=False)
    # these largely convert the "chosen/not chosen" into "Yes/No" etc and other similar parsing of encoded characters

    print(
        "Finished! All additional data added. Remember to re-run and update the stats if you want to see the updated"
        "research data from these additional sessions in the UI - the scores will only calculate when the stats update"
        "gets ran (e.g. by running async_update_stats or using the endpoint for update-stats/{incremental_update})"
    )


if __name__ == "__main__":
    asyncio.run(align_additional_data_to_current_answers())
