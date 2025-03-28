import pytest

from mondey_backend.import_data.utils import generate_parents_for_children


@pytest.mark.asyncio
async def test_creating_parents_for_children():
    child_ids = [159, 202]
    child_parent_dict = await generate_parents_for_children(child_ids)
    assert len(child_parent_dict.keys()) == 2
    assert child_parent_dict[159] == 1
    assert child_parent_dict[202] == 2
