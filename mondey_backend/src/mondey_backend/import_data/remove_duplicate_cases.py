import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from mondey_backend.import_data.utils import check_parent_exists
from mondey_backend.models.children import Child


async def remove_duplicate_cases(
    csv_data: pd.DataFrame, session: Session, user_session: AsyncSession
) -> tuple[pd.DataFrame, list[str]]:
    """
    Remove duplicate cases from the additional data CSV.

    A case is considered a duplicate if there is already a child in the database
    with the same CASE ID and a parent user with an email containing exactly our template with the child's CASE ID.

    Args:
        csv_data: DataFrame containing the additional data
        session: SQLAlchemy session for database operations
        user_session: Async SQLAlchemy session for user operations

    Returns:
        Tuple containing:
            - The filtered DataFrame with duplicates removed
            - List of CASE IDs that were identified as duplicates and removed
    """
    print(f"Original data contains {len(csv_data)} rows")

    case_ids = csv_data["CASE"].astype(str).unique().tolist()

    duplicate_case_ids = []
    # Check each CASE ID for duplicates
    for case_id in case_ids:
        # Check if a child with this CASE ID exists in the database
        imported_child_name = f"Imported Child {case_id}"
        print("Looked up: ", imported_child_name)
        existing_child = session.exec(
            select(Child).where(col(Child.name) == imported_child_name)
        ).first()

        if existing_child:
            # Check if there's a parent user with an email containing the child's CASE ID
            existing_parent = await check_parent_exists(user_session, case_id)

            if existing_parent:
                # Both child and parent exist, this is a duplicate
                duplicate_case_ids.append(case_id)
                print(f"Found duplicate CASE ID: {case_id}")

    # Filter out rows with duplicate CASE IDs
    filtered_df = csv_data[~csv_data["CASE"].astype(str).isin(duplicate_case_ids)]

    print(f"Removed {len(duplicate_case_ids)} duplicate cases")
    print(f"Filtered data contains {len(filtered_df)} rows")

    return filtered_df, duplicate_case_ids
