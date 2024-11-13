import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "client_type", ["public_client", "user_client", "research_client", "admin_client"]
)
def test_get_languages(client_type: str, request: pytest.FixtureRequest):
    client = request.getfixturevalue(client_type)
    response = client.get("/languages/")
    assert response.status_code == 200
    assert response.json() == ["de", "en", "fr"]


def test_get_milestone_groups_child1(
    user_client: TestClient, milestone_group1: dict, milestone_group2: dict
):
    response = user_client.get("/milestone-groups/1")
    assert response.status_code == 200
    assert len(response.json()) == 2
    # child 1 age is ~9 months old, so no milestones from group2
    milestone_group2["milestones"] = []
    # and only last two milestones (6m, 12m) from group1:
    milestone_group1["milestones"] = milestone_group1["milestones"][1:]
    assert response.json() == [milestone_group2, milestone_group1]


def test_get_milestone_groups_child2(
    user_client: TestClient, milestone_group1: dict, milestone_group2: dict
):
    response = user_client.get("/milestone-groups/2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    # child 2 age is 20 months old, so first milestone from group1 (18m):
    milestone_group1["milestones"] = milestone_group1["milestones"][0:1]
    milestone_group1["progress"] = 0.0

    # and first milestone from group2 (24m):
    milestone_group2["milestones"] = milestone_group2["milestones"][0:1]
    assert response.json() == [milestone_group2, milestone_group1]


def test_get_milestone_groups_child3(
    admin_client: TestClient, milestone_group1: dict, milestone_group2: dict
):
    response = admin_client.get("/milestone-groups/3")
    assert response.status_code == 200
    assert len(response.json()) == 2
    # child 3 age is ~60 months old, so no milestones
    milestone_group1["milestones"] = []
    # and first last milestone from group2 (24m):
    milestone_group2["milestones"] = []
    milestone_group2["progress"] = 0.0
    milestone_group1["progress"] = 0.0
    assert response.json() == [milestone_group2, milestone_group1]


def test_get_milestone_groups_child_doesnt_belong_to_user(
    research_client: TestClient,
):
    response = research_client.get("/milestone-groups/1")
    assert response.status_code == 404


def test_get_milestone_groups_invalid_child_id(
    research_client: TestClient,
):
    response = research_client.get("/milestone-groups/99")
    assert response.status_code == 404
