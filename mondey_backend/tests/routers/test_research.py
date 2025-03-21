from fastapi.testclient import TestClient


def test_research_data_invalid_user(user_client: TestClient):
    response = user_client.get("/research/data/")
    assert response.status_code == 401


def test_research_data(research_client: TestClient):
    response = research_client.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # only answers from children of users in the same research group should be included
    assert len(data) == 4
    for item in data:
        assert item["Was noch?"] == "other"
        assert item["was?"] == "a"


def test_research_data_full_data_access(research_client_full_data_access: TestClient):
    response = research_client_full_data_access.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # all answers (excluding those from test users) are included
    assert len(data) == 5
