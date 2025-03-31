import smtplib
from email.message import EmailMessage

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from mondey_backend.dependencies import UserAsyncSessionDep
from mondey_backend.models.users import User


class SMTPMock:
    last_message: EmailMessage | None = None
    username: str | None = None
    password: str | None = None

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send_message(self, msg: EmailMessage, **kwargs):
        SMTPMock.last_message = msg

    def login(self, username: str, password: str):
        SMTPMock.username = username
        SMTPMock.password = password


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
    assert smtp_mock.username == "test-smtp-username"
    assert smtp_mock.password == "test-smtp-password"
    assert "aktivieren" in msg.get("Subject").lower()
    assert msg.get("To") == email
    assert "/verify/" in msg.get_content()
    response = public_client.post("/auth/verify", json={"token": "invalid-token"})
    assert response.status_code == 400
    token = msg.get_content().split("\n\n")[1].rsplit("/")[-1]
    response = public_client.post("/auth/verify", json={"token": token})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_test_account(
    public_client: TestClient, smtp_mock: SMTPMock, user_session: UserAsyncSessionDep
):
    assert smtp_mock.last_message is None
    email = "2349812.12234987tester@testaccount.com"
    response = public_client.post(
        "/auth/register", json={"email": email, "password": "p1"}
    )
    assert response.status_code == 201
    msg = smtp_mock.last_message
    assert (
        msg is None
    )  # we want no last message, because it should not email upon test account registrations.

    user_query = select(User).where(User.email == email)
    result = await user_session.execute(user_query)
    user = result.scalars().first()

    assert user is not None
    assert user.is_verified is True


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


def test_user_reset_password(user_client: TestClient, smtp_mock: SMTPMock):
    assert smtp_mock.last_message is None
    email = "user@mondey.de"
    response = user_client.post("/auth/forgot-password", json={"email": email})
    assert response.status_code == 202

    msg = smtp_mock.last_message
    assert msg is not None
    assert msg.get("To") == email
    token = msg.get_content().split("\n\n")[1].rsplit("/")[-1]
    new_password = "new_password"
    response = user_client.post(
        "/auth/reset-password", json={"token": token, "password": new_password}
    )
    assert response.status_code == 200


def test_user_reset_password_invalid_token(
    user_client: TestClient, smtp_mock: SMTPMock
):
    assert smtp_mock.last_message is None
    email = "user@mondey.de"
    response = user_client.post("/auth/forgot-password", json={"email": email})
    assert response.status_code == 202

    msg = smtp_mock.last_message
    assert msg is not None
    assert msg.get("To") == email
    token = msg.get_content().split("\n\n")[1].rsplit("/")[-1] + "invalid"
    new_password = "new_password"
    response = user_client.post(
        "/auth/reset-password", json={"token": token, "password": new_password}
    )
    assert response.status_code == 400


def test_user_forgot_password(
    user_client: TestClient, active_user, smtp_mock: SMTPMock
):
    assert smtp_mock.last_message is None
    response = user_client.post(
        "/auth/forgot-password", json={"email": active_user.email}
    )
    assert response.status_code == 202


def test_user_forgot_password_invalid_email(
    user_client: TestClient, smtp_mock: SMTPMock
):
    assert smtp_mock.last_message is None
    email = "invalid-email"
    response = user_client.post("/auth/forgot-password", json={"email": email})
    assert "@" in response.json()["detail"][0]["msg"]
    assert response.json()["detail"][0]["type"] == "value_error"
