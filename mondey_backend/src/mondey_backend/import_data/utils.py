import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from mondey_backend.models.users import User

# here to avoid circular import
# 1. Because it's logical to do the deduplication code in data_manager
# 2. But data_manager is imported from import_manager, so we can't just keep this in either of those two
# 3. and still have it be accessibel to the remove_duplicate_cases.py code.
# I think this pattern of utils.py for this fits consistently with the rest of our code.


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

    # Values in the survey contain optional whitespace, suffixes such as
    # "SSW"/"Woche", and occasionally a trailing decimal point. The leading
    # number is the pregnancy duration; a number after "+" or "," is the
    # associated incubator-weeks value used by the existing data model.
    match = re.match(r"^\s*(\d+)(?:\s*\.?\s*[+,]\s*(\d+))?", str(birth_term))
    if match is None:
        return (0, 0)

    birth_weeks = int(match.group(1))
    incubator_weeks = int(match.group(2)) if match.group(2) else 0
    return (birth_weeks, incubator_weeks)
