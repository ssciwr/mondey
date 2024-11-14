from fastapi.testclient import TestClient


def test_users(admin_client: TestClient):
    response = admin_client.get("/admin/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 4
    assert users[0]["id"] == 1
    assert not users[0]["is_researcher"]
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
