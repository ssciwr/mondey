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
from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.import_data.utils import labels_path
from mondey_backend.import_data.utils import milestones_metadata_path
from mondey_backend.import_data.utils import questions_configured_path

"""
Once the files in utils have been put in this directory, this file imports all data from start to finish.

You will usually want to clear the (import-specific) database each time you run this. To do that, run
`python3 -m import_all.py true`. This will wipe whatever is in the import_data/db databases in terms of data.
"""

if __name__ == "__main__":
    import_current_session, import_current_engine = get_import_current_session()

    import_milestones_metadata(import_current_session, milestones_metadata_path)

    print("Now assigning children their milestones")
    map_children_milestones_data(data_path, import_current_session)
    print("Done assigning children their milestones.")

    print("Now setting the custom question/answers pairs")
    import_childrens_question_answers_data(
        import_current_session,
        labels_path,
        data_path,
        questions_configured_path,
        clear_existing_questions_and_answers=False,
    )

"""
Todos to make this work for the second masters batch of data (obviously it'll be hard to be sure it can work with the
amount of different columns, ways they work, and the possibility of changed data collection):

- Add code to merge the sibling answers (by setting # younger/older siblings to 0 if none)
for child_id in child_ids:\n",
    "    with con:\n",
    "        cur = con.cursor()\n",
    "        for question_id in [17, 18]:\n",
    "            if not cur.execute(\n",
    "                f\"select * from childanswer where child_id={child_id} and question_id={question_id}\"\n",
    "            ).fetchone():\n",
    "                sql = f\"insert into childanswer values (0, NULL, {child_id}, {question_id});\"\n",
    "                print(sql)\n",
    "                cur.execute(sql)"
- Add code after that to delete the "Do you have siblings?" kind of question.

- Replace parsed text in questions/answers (correct_answers.py)

- Merge the Eltern question

- Change exceptio nfor ANdere Diagnosen.

- x textarea/text in make_text_question.


"""
