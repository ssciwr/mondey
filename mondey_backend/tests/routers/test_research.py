from fastapi.testclient import TestClient


def test_research_data_invalid_user(user_client: TestClient):
    response = user_client.get("/research/data/")
    assert response.status_code == 401


def test_research_data(research_client: TestClient):
    response = research_client.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # only answer sessions from children of users in the same research group should be included
    assert len(data) == 2
    for item in data:
        assert item["user_question_1"] == "lorem ipsum"
        # for user question 2, the answer is "other" which is the additional_option for this question,
        # so we get the additional_answer here instead of the answer:
        assert item["user_question_2"] == "dolor sit"
        assert item["child_question_1"] == "a"
        assert item["child_question_2"] == "apple"
        assert "milestone_id_1" in item


def test_research_data_full_data_access(research_client_full_data_access: TestClient):
    response = research_client_full_data_access.get("/research/data/")
    assert response.status_code == 200
    data = response.json()
    # all three answer sessions (excluding those from test users) are included
    assert len(data) == 3


def test_research_data_deleted_child(admin_client: TestClient):
    # admin client has 1 child, sees all 3 answer sessions:
    assert len(admin_client.get("/users/children/").json()) == 1
    assert len(admin_client.get("/research/data/").json()) == 3
    # if a child is deleted, their answers are no longer included
    assert admin_client.delete("/users/children/3").status_code == 200
    assert len(admin_client.get("/users/children/").json()) == 0
    assert len(admin_client.get("/research/data/").json()) == 2


def test_research_names(research_client: TestClient):
    response = research_client.get("/research/names/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert "milestone" in data
    assert "user_question" in data
    assert "child_question" in data
    assert len(data["milestone"]) == 5
    assert data["milestone"]["1"] == "m1"
    assert data["milestone"]["5"] == "m5"
    assert len(data["user_question"]) == 2
    assert data["user_question"]["1"] == "User Question 1"
    assert data["user_question"]["2"] == "User Question 2"
    assert len(data["child_question"]) == 2
    assert data["child_question"]["1"] == "Child Question 1"
    assert data["child_question"]["2"] == "Child Question 2"
