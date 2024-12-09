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
