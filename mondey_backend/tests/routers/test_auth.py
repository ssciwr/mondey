import smtplib
from email.message import EmailMessage

import pytest
from fastapi.testclient import TestClient


class SMTPMock:
    last_message: EmailMessage | None = None

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send_message(self, msg: EmailMessage, **kwargs):
        SMTPMock.last_message = msg


@pytest.fixture
def smtp_mock(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(smtplib, "SMTP", SMTPMock)
    SMTPMock.last_message = None
    return SMTPMock


def test_register_new_user(public_client: TestClient, smtp_mock: SMTPMock):
    assert smtp_mock.last_message is None
    email = "u1@asdgdasf.com"
    response = public_client.post(
        "/auth/register", json={"email": email, "password": "p1"}
    )
    assert response.status_code == 201
    msg = smtp_mock.last_message
    assert msg is not None
    assert "aktivieren" in msg.get("Subject").lower()
    assert msg.get("To") == email
    assert "/verify/" in msg.get_content()
    response = public_client.post("/auth/verify", json={"token": "invalid-token"})
    assert response.status_code == 400
    token = msg.get_content().split("\n\n")[1].rsplit("/")[-1]
    response = public_client.post("/auth/verify", json={"token": token})
    assert response.status_code == 200


def test_register_new_user_invalid_research_code_ignored(
    admin_client: TestClient, smtp_mock: SMTPMock
):
    email = "a@b.com"
    response = admin_client.post(
        "/auth/register",
        json={"email": email, "password": "p1", "research_group_id": 703207},
    )
    assert response.status_code == 201
    new_user = admin_client.get("/admin/users/").json()[-1]
    assert new_user["email"] == email
    assert new_user["research_group_id"] == 0


def test_register_new_user_valid_research_code(
    admin_client: TestClient, smtp_mock: SMTPMock
):
    email = "a@b.com"
    response = admin_client.post(
        "/auth/register",
        json={"email": email, "password": "p1", "research_group_id": 123451},
    )
    assert response.status_code == 201
    new_user = admin_client.get("/admin/users/").json()[-1]
    assert new_user["email"] == email
    assert new_user["research_group_id"] == 123451
