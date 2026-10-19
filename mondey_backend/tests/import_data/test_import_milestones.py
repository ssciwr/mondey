from unittest.mock import AsyncMock

import pandas as pd
import pytest
from sqlmodel import select

from mondey_backend.import_data.manager.import_manager import ImportManager
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAnswerSession


@pytest.mark.asyncio
async def test_import_milestones_links_persisted_ids(session, user_session):
    manager = ImportManager(session=session, user_session=user_session)
    manager.generate_parents_for_children = AsyncMock(return_value={"999": 3})
    data = pd.DataFrame(
        [{"CASE": 999, "FK01": 1, "FK02": 1, "STARTED": "2024-07-15 12:00:00", "m1": 4}]
    )

    assert await manager.import_children_with_milestone_data(data) == 1
    child = session.exec(select(Child).where(Child.name == "Imported Child 999")).one()
    answer_session = session.exec(
        select(MilestoneAnswerSession).where(
            MilestoneAnswerSession.child_id == child.id
        )
    ).one()
    assert child.id is not None
    assert answer_session.child_id == child.id
    assert answer_session.answers[1].milestone_group_id == 1
    assert answer_session.answers[1].answer == 3


@pytest.mark.asyncio
async def test_import_milestones_rejects_missing_group(session, user_session):
    milestone = session.get(Milestone, 1)
    milestone.group_id = None
    manager = ImportManager(session=session, user_session=user_session)
    manager.generate_parents_for_children = AsyncMock()

    with pytest.raises(ValueError, match="Milestone m1 must have an ID and group ID"):
        await manager.import_children_with_milestone_data(pd.DataFrame())
    manager.generate_parents_for_children.assert_not_called()
