import pytest


@pytest.mark.parametrize(
    "client_type", ["user_client", "research_client", "admin_client"]
)
class TestMilestones:
    def test_get_languages(self, client_type: str, request: pytest.FixtureRequest):
        client = request.getfixturevalue(client_type)
        response = client.get("/languages/")
        assert response.status_code == 200
        assert response.json() == {"de": 1, "en": 2, "fr": 3}

    def test_get_milestone_groups(
        self,
        client_type: str,
        milestone_group1: dict,
        milestone_group2: dict,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-groups/")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json() == [milestone_group2, milestone_group1]

    def test_get_milestone_group(
        self,
        client_type: str,
        milestone_group1: dict,
        milestone_group2: dict,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response1 = client.get("/milestone-groups/1")
        assert response1.status_code == 200
        assert response1.json() == milestone_group1
        response2 = client.get("/milestone-groups/2")
        assert response2.status_code == 200
        assert response2.json() == milestone_group2

    def test_get_milestone_group_invalid_id(
        self, client_type: str, request: pytest.FixtureRequest
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-groups/99")
        assert response.status_code == 404
