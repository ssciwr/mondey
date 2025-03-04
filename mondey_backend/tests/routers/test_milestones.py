import pathlib

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

    # and first milestone from group2 (24m):
    milestone_group2["milestones"] = milestone_group2["milestones"][0:1]
    assert response.json() == [milestone_group2, milestone_group1]


def test_get_milestone_groups_child3(
    admin_client: TestClient, milestone_group1: dict, milestone_group2: dict
):
    response = admin_client.get("/milestone-groups/3")
    assert response.status_code == 200
    assert len(response.json()) == 2
    milestone_group1["milestones"] = []
    milestone_group2["milestones"] = milestone_group2["milestones"][1:]

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


def test_order_milestones_and_milestone_groups_child1(
    admin_client: TestClient, milestone_group1: dict, milestone_group2: dict
):
    milestone_groups = admin_client.get("/milestone-groups/1").json()
    # initial milestone group order:
    assert milestone_groups[0]["id"] == 2
    assert milestone_groups[1]["id"] == 1
    # initial milestone order within group1:
    assert milestone_groups[1]["milestones"][0]["id"] == 2
    assert milestone_groups[1]["milestones"][1]["id"] == 1
    # re-order milestone groups
    response = admin_client.post(
        "/admin/milestone-groups/order/",
        json=[{"id": 1, "order": 0}, {"id": 2, "order": 1}],
    )
    assert response.status_code == 200
    # re-order milestones
    response = admin_client.post(
        "/admin/milestones/order/",
        json=[{"id": 2, "order": 1}, {"id": 1, "order": 0}, {"id": 3, "order": 2}],
    )
    assert response.status_code == 200
    milestone_groups = admin_client.get("/milestone-groups/1").json()
    # new milestone group order:
    assert milestone_groups[0]["id"] == 1
    assert milestone_groups[1]["id"] == 2
    # new milestone order within group1:
    assert milestone_groups[0]["milestones"][0]["id"] == 1
    assert milestone_groups[0]["milestones"][1]["id"] == 2


def test_submit_milestone_image_invalid_milestone(
    user_client: TestClient, image_file_jpg_1600_1200: pathlib.Path
):
    with open(image_file_jpg_1600_1200, "rb") as f:
        response = user_client.post(
            "/submitted-milestone-images/99",
            files={"file": ("img.jpg", f, "image/jpeg")},
        )
    assert response.status_code == 404


def test_submit_milestone_image_valid(
    user_client: TestClient,
    image_file_jpg_1600_1200: pathlib.Path,
    static_dir: pathlib.Path,
):
    submitted_image_file = static_dir / "ms" / "3.webp"
    assert not submitted_image_file.is_file()
    with open(image_file_jpg_1600_1200, "rb") as f:
        response = user_client.post(
            "/submitted-milestone-images/1",
            files={"file": ("img.jpg", f, "image/jpeg")},
        )
    assert response.status_code == 200
    assert submitted_image_file.is_file()
