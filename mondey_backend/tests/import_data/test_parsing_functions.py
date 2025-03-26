from mondey_backend.import_data.import_milestones_metadata import (
    derive_milestone_group_from_milestone_string_id,
)


def test_milestone_group_lookups():
    assert derive_milestone_group_from_milestone_string_id("DE23") == "Denken"
    assert derive_milestone_group_from_milestone_string_id("SP_3987") == "Sprache"
    assert derive_milestone_group_from_milestone_string_id("5466") is None
    assert derive_milestone_group_from_milestone_string_id("D") is None
