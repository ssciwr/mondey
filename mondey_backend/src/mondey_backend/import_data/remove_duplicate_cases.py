import pandas as pd
from sqlalchemy.orm import Session
from sqlmodel import col

from mondey_backend.import_data.utils import additional_data_path
from mondey_backend.import_data.utils import get_import_current_session
from mondey_backend.models.children import Child
from mondey_backend.models.users import User


def remove_duplicate_cases(
    additional_data_path: str, session: Session, output_path: str | None = None
) -> tuple[pd.DataFrame, list[str]]:
    """
    Remove duplicate cases from the additional data CSV.

    A case is considered a duplicate if there is already a child in the database
    with the same CASE ID and a parent user with an email containing exactly our template with the child's CASE ID.

    Args:
        additional_data_path: Path to the additional data CSV file
        session: SQLAlchemy session for database operations
        output_path: Path to save the filtered CSV (optional)

    Returns:
        Tuple containing:
            - The filtered DataFrame with duplicates removed
            - List of CASE IDs that were identified as duplicates and removed
    """
    additional_data_df = pd.read_csv(
        additional_data_path, sep="\t", encoding="utf-16", encoding_errors="replace"
    )

    print(f"Original data contains {len(additional_data_df)} rows")

    case_ids = additional_data_df["CASE"].astype(str).unique().tolist()

    duplicate_case_ids = []

    # Check each CASE ID for duplicates
    for case_id in case_ids:
        # Check if a child with this CASE ID exists in the database
        imported_child_name = f"Imported Child {case_id}"
        existing_child = (
            session.query(Child).where(col(Child.name) == imported_child_name).first()
        )

        if existing_child:
            # Check if there's a parent user with an email containing the child's CASE ID
            parent_email_pattern = f"parent_of_{case_id}@artificialimporteddata.csv"
            existing_parent = (
                session.query(User).where(User.email == parent_email_pattern).first()
            )

            if existing_parent:
                # Both child and parent exist, this is a duplicate
                duplicate_case_ids.append(case_id)
                print(f"Found duplicate CASE ID: {case_id}")

    # Filter out rows with duplicate CASE IDs
    filtered_df = additional_data_df[
        ~additional_data_df["CASE"].astype(str).isin(duplicate_case_ids)
    ]

    print(f"Removed {len(duplicate_case_ids)} duplicate cases")
    print(f"Filtered data contains {len(filtered_df)} rows")

    if output_path:
        filtered_df.to_csv(output_path, sep="\t", encoding="utf-16", index=False)
        print(f"Filtered data saved to {output_path}")

    return filtered_df, duplicate_case_ids


if __name__ == "__main__":
    # Get database session
    import_current_session, _ = get_import_current_session()

    # Define output path for filtered data
    filtered_output_path = additional_data_path.replace(".csv", "_filtered.csv")

    # Remove duplicates and save filtered data
    _, duplicate_cases = remove_duplicate_cases(
        additional_data_path, import_current_session, filtered_output_path
    )

    print(f"Duplicate CASE IDs removed: {duplicate_cases}")
