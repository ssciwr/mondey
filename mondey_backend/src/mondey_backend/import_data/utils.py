# here to avoid circular import
# 1. Because it's logical to do the deduplication code in data_manager
# 2. But data_manager is imported from import_manager, so we can't just keep this in either of those two
# 3. and still have it be accessibel to the remove_duplicate_cases.py code.
# I think this pattern of utils.py for this fits consistently with the rest of our code.


from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from mondey_backend.models.users import User


async def check_parent_exists(user_session: AsyncSession, case_id: int) -> User | None:
    """Check if a parent exists for a child."""
    email = f"parent_of_{case_id}@artificialimporteddata.csv"

    stmt = select(User).where(User.email == email)
    result = await user_session.execute(stmt)
    existing_parent = result.scalars().first()

    return existing_parent


def parse_weeks(birth_term):
    # Handle empty or None values
    if not birth_term or birth_term == "<null>":
        return (0, 0)

    # Clean the input string
    birth_term = birth_term.strip()

    # Check for "+" or "," separator indicating incubator weeks
    separators = ["+", ","]
    for sep in separators:
        if sep in birth_term:
            parts = [p.strip() for p in birth_term.split(sep)]
            try:
                birth_weeks = int(parts[0])
                incubator_weeks = int(parts[1])
                return (birth_weeks, incubator_weeks)
            except (ValueError, IndexError):
                print(f"Warning: Could not parse '{birth_term}' with separator '{sep}'")

    # If no separator found, assume it's just the birth weeks
    try:
        birth_weeks = int(birth_term)
        return (birth_weeks, 0)
    except ValueError:
        print(f"Warning: Could not parse '{birth_term}' as an integer")
        return (0, 0)
