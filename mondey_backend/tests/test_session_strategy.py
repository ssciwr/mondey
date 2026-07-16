from __future__ import annotations

import datetime
from types import SimpleNamespace

import pytest
from fastapi import Response

from mondey_backend.settings import app_settings
from mondey_backend.users import SESSION_ABSOLUTE_EXPIRES_HEADER
from mondey_backend.users import SESSION_IDLE_EXPIRES_HEADER
from mondey_backend.users import SessionDatabaseStrategy


class FakeAccessTokenDatabase:
    def __init__(self, access_token):
        self.access_token = access_token
        self.tokens = {access_token.token: access_token}
        self.updates = []
        self.deleted = False

    async def get_by_token(self, token, max_age=None):
        return self.tokens.get(token)

    async def create(self, create_dict):
        now = datetime.datetime.now(datetime.UTC)
        access_token = SimpleNamespace(
            token="new-token",
            user_id=create_dict["user_id"],
            created_at=now,
            last_seen_at=now,
        )
        self.tokens[access_token.token] = access_token
        return access_token

    async def update(self, access_token, update_dict):
        self.updates.append(update_dict)
        for key, value in update_dict.items():
            setattr(access_token, key, value)
        return access_token

    async def delete(self, access_token):
        self.deleted = True
        self.tokens.pop(access_token.token, None)


class FakeUserManager:
    def parse_id(self, user_id):
        return int(user_id)

    async def get(self, user_id):
        return SimpleNamespace(id=user_id)


@pytest.fixture
def session_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(app_settings, "SESSION_IDLE_TIMEOUT_SECONDS", 60)
    monkeypatch.setattr(app_settings, "SESSION_ABSOLUTE_TIMEOUT_SECONDS", 120)
    monkeypatch.setattr(app_settings, "SESSION_TOUCH_INTERVAL_SECONDS", 10)
    monkeypatch.setattr(app_settings, "SESSION_WARNING_SECONDS", 15)


def make_access_token(*, created_seconds_ago=0, seen_seconds_ago=0):
    now = datetime.datetime.now(datetime.UTC)
    return SimpleNamespace(
        token="token",
        user_id=7,
        created_at=now - datetime.timedelta(seconds=created_seconds_ago),
        last_seen_at=now - datetime.timedelta(seconds=seen_seconds_ago),
    )


@pytest.mark.asyncio
async def test_active_session_is_touched_and_headers_are_returned(session_settings):
    access_token = make_access_token(created_seconds_ago=30, seen_seconds_ago=20)
    database = FakeAccessTokenDatabase(access_token)
    response = Response()
    strategy = SessionDatabaseStrategy(database, response)

    user = await strategy.read_token("token", FakeUserManager())

    assert user.id == 7
    assert len(database.updates) == 1
    assert SESSION_IDLE_EXPIRES_HEADER in response.headers
    assert SESSION_ABSOLUTE_EXPIRES_HEADER in response.headers


@pytest.mark.asyncio
async def test_idle_session_expires(session_settings):
    database = FakeAccessTokenDatabase(make_access_token(seen_seconds_ago=61))
    strategy = SessionDatabaseStrategy(database)

    assert await strategy.read_token("token", FakeUserManager()) is None
    assert database.deleted


@pytest.mark.asyncio
async def test_absolute_timeout_cannot_be_extended_by_activity(session_settings):
    database = FakeAccessTokenDatabase(
        make_access_token(created_seconds_ago=121, seen_seconds_ago=1)
    )
    strategy = SessionDatabaseStrategy(database)

    assert await strategy.read_token("token", FakeUserManager()) is None
    assert database.deleted


@pytest.mark.asyncio
async def test_reauthentication_rotates_token_and_resets_absolute_timeout(
    session_settings,
):
    old_access_token = make_access_token(created_seconds_ago=100, seen_seconds_ago=1)
    database = FakeAccessTokenDatabase(old_access_token)
    strategy = SessionDatabaseStrategy(database)

    rotated = await strategy.rotate_session("token", SimpleNamespace(id=7))

    assert rotated is not None
    new_token, session_info = rotated
    assert new_token == "new-token"
    assert "token" not in database.tokens
    assert "new-token" in database.tokens
    assert session_info.absolute_expires_at > datetime.datetime.now(
        datetime.UTC
    ) + datetime.timedelta(seconds=119)
