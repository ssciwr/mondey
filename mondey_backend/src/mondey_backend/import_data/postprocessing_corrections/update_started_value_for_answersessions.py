# Implements https://github.com/ssciwr/mondey/pull/284/commits/3d3d789b75fe0bf5cdd6a037e7c9ce7e2d745866
"""
Script to add STARTED dates from data.csv to MilestoneAnswerSessions in database
"""

import pandas as pd

from mondey_backend.import_data.utils import data_path
from mondey_backend.import_data.utils import get_import_current_session


def update_started_value_for_answersessions(relevant_data_csv_path: str):
    # Read the CSV file
    df = pd.read_csv(
        relevant_data_csv_path,
        encoding="utf-16",
        sep="\t",
    )

    # Select only the CASE and STARTED columns and set CASE as index
    df = (df.loc[:, ["CASE", "STARTED"]]).set_index("CASE")

    # Get database session
    session, engine = get_import_current_session()

    # Update MilestoneAnswerSession records
    for child_id, row in df.iterrows():
        print(f"Updating child_id {child_id} with STARTED date {row.STARTED}")
        session.execute(
            f"UPDATE milestoneanswersession SET created_at='{row.STARTED}' WHERE child_id={child_id}"
        )

    # Commit the changes
    session.commit()

    print("Successfully updated MilestoneAnswerSession records with STARTED dates")


if __name__ == "__main__":
    update_started_value_for_answersessions(data_path)
