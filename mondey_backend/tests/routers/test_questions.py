from fastapi.testclient import TestClient


def test_get_child_questions(user_client: TestClient):
    response = user_client.get("/child-questions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_questions(user_client: TestClient):
    response = user_client.get("/user-questions/")
    assert response.status_code == 200
    assert len(response.json()) == 2
