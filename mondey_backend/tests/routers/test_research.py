from fastapi.testclient import TestClient


def test_auth_invalid_user(user_client: TestClient):
    response = user_client.get("/research/auth/")
    assert response.status_code == 401


def test_auth(research_client: TestClient):
    response = research_client.get("/research/auth/")
    assert response.status_code == 200
