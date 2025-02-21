from checkdigit import verhoeff
from fastapi.testclient import TestClient


def test_users(admin_client: TestClient):
    response = admin_client.get("/admin/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 5
    assert users[0]["id"] == 1
    assert users[0]["is_researcher"]
    assert users[0]["is_superuser"]
    assert users[1]["id"] == 2
    assert users[1]["is_researcher"]
    assert not users[1]["is_superuser"]
    assert users[2]["id"] == 3
    assert not users[2]["is_researcher"]
    assert not users[2]["is_superuser"]
    assert users[3]["id"] == 4
    assert not users[3]["is_researcher"]
    assert not users[3]["is_superuser"]
    assert users[4]["id"] == 5
    assert "tester@testaccount.com" in users[4]["email"]
    assert not users[4]["is_researcher"]
    assert not users[4]["is_superuser"]


def test_get_research_groups(admin_client: TestClient):
    response = admin_client.get("/admin/research-groups/")
    assert response.status_code == 200
    research_groups = response.json()
    assert research_groups == [{"id": 123451}]


def test_delete_research_group(admin_client: TestClient):
    response = admin_client.delete("/admin/research-groups/123451")
    assert response.status_code == 200
    assert admin_client.get("/admin/research-groups/").json() == []


def test_create_research_group(admin_client: TestClient):
    research_group = {"id": 123451}
    assert admin_client.get("/admin/research-groups/").json() == [research_group]
    response = admin_client.post("/admin/research-groups/2")
    assert response.status_code == 200
    new_research_group = response.json()
    assert verhoeff.validate(str(new_research_group["id"]))
    new_groups = admin_client.get("/admin/research-groups/").json()
    assert len(new_groups) == 2
    assert research_group in new_groups
    assert new_research_group in new_groups
