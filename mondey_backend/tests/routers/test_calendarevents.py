from fastapi.testclient import TestClient


def test_calendar_events_accessible(user_client: TestClient):
    response = user_client.get("/events/")
    assert response.status_code == 200
