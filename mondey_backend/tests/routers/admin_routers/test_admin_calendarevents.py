from fastapi.testclient import TestClient


# we use the year 3025 so these will for our intents and purposes always be in the future, for example asserting
# that some calendar event we just added can be retrieved using the /get general route.
def test_create_get_update_calendar_event(admin_client: TestClient):
    response = admin_client.get("/events/")
    assert response.status_code == 200
    assert response.json() == []

    event_data = {
        "title": "Digitale Medien und Kinderpsychologie",
        "description": "Ein Expertenpanel diskutiert die Auswirkungen von Bildschirmzeit und sozialen Medien auf die kindliche Entwicklung.",
        "external_link": "https://example.com/event",
        "event_date": "3025-11-15",
    }

    response = admin_client.post("/admin/calendarevents/", json=event_data)
    assert response.status_code == 200
    created_event = response.json()
    assert created_event["title"] == event_data["title"]
    assert created_event["description"] == event_data["description"]
    assert created_event["external_link"] == event_data["external_link"]
    assert created_event["event_date"] == "3025-11-15T00:00:00"
    assert "id" in created_event
    event_id = created_event["id"]

    response = admin_client.get("/events/")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["id"] == event_id
    assert events[0]["title"] == event_data["title"]

    update_data = {"event_date": "3025-12-20"}
    response = admin_client.put(f"/admin/calendarevents/{event_id}", json=update_data)
    assert response.status_code == 200
    updated_event = response.json()
    assert updated_event["id"] == event_id
    assert updated_event["event_date"] == "3025-12-20T00:00:00"
    assert updated_event["title"] == event_data["title"]

    response = admin_client.get("/events/")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["event_date"] == "3025-12-20T00:00:00"


def test_delete_calendar_event(admin_client: TestClient):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "external_link": "https://test.com",
        "event_date": "3025-01-01",
    }
    response = admin_client.post("/admin/calendarevents/", json=event_data)
    assert response.status_code == 200
    event_id = response.json()["id"]

    response = admin_client.get("/events/")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = admin_client.delete(f"/admin/calendarevents/{event_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    response = admin_client.get("/events/")
    assert response.status_code == 200
    assert response.json() == []


def test_calendar_events_non_admin_cannot_modify(user_client: TestClient):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "external_link": "https://test.com",
        "event_date": "3025-01-01",
    }

    response = user_client.post("/admin/calendarevents/", json=event_data)
    assert response.status_code == 401
