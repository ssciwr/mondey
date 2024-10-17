import pytest


@pytest.mark.parametrize(
    "client_type", ["public_client", "user_client", "research_client", "admin_client"]
)
class TestMilestones:
    def test_get_languages(self, client_type: str, request: pytest.FixtureRequest):
        client = request.getfixturevalue(client_type)
        response = client.get("/languages/")
        assert response.status_code == 200
        assert response.json() == {"de": 1, "en": 2, "fr": 3}

    def test_get_milestone_groups_age_group_1(
        self,
        client_type: str,
        milestone_group1: dict,
        milestone_group2: dict,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-groups/?milestone_age_group_id=1")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json() == [milestone_group2, milestone_group1]

    def test_get_milestone_groups_age_group_2(
        self,
        client_type: str,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-groups/?milestone_age_group_id=2")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_milestone_groups_invalid_age_group(
        self,
        client_type: str,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-groups/?milestone_age_group_id=67")
        assert response.status_code == 200
        assert response.json() == []

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

    def test_get_milestone_age_groups(
        self,
        client_type: str,
        milestone_group1: dict,
        milestone_group2: dict,
        request: pytest.FixtureRequest,
    ):
        client = request.getfixturevalue(client_type)
        response = client.get("/milestone-age-groups/")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json() == [
            {"id": 1, "months_min": 0, "months_max": 36},
            {"id": 2, "months_min": 36, "months_max": 72},
        ]
