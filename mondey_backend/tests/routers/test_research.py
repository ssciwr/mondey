from fastapi.testclient import TestClient


def test_research_data_invalid_user(user_client: TestClient):
    response = user_client.get("/research/data/")
    assert response.status_code == 401


def test_research_data(research_client: TestClient):
    response = research_client.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # only answers from children of users in the same research group should be included
    user_ids_with_research_id = [2, 3, 5]
    assert len(data) == 4
    for item in data:
        assert item["user_id"] in user_ids_with_research_id
        assert item["child_id"] == 1
        assert item["[Beobachter] Was noch?"] == "other"
        assert item["[Kind] was?"] == "a"


def test_research_data_full_data_access(research_client_full_data_access: TestClient):
    response = research_client_full_data_access.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # all answers are included
    assert len(data) == 5
