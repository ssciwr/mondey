from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI
from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mondey_backend.models.users import AccessToken
from mondey_backend.models.users import User
from mondey_backend.users import SESSION_ABSOLUTE_EXPIRES_HEADER
from mondey_backend.users import SESSION_IDLE_EXPIRES_HEADER
from mondey_backend.users import cookie_transport


@pytest.mark.asyncio
async def test_reauthentication_verifies_password_and_rotates_session(
    app: FastAPI,
    user_session: AsyncSession,
):
    password = "correct horse battery staple"
    user = await user_session.get(User, 3)
    assert user is not None
    user.hashed_password = PasswordHelper().hash(password)
    await user_session.commit()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="https://testserver",
    ) as client:
        login_response = await client.post(
            "/auth/login",
            data={"username": user.email, "password": password},
        )
        assert login_response.status_code == 204
        old_token = client.cookies.get(cookie_transport.cookie_name)
        assert old_token is not None

        bad_password_response = await client.post(
            "/auth/session/reauthenticate",
            json={"password": "wrong password"},
        )
        assert bad_password_response.status_code == 400
        assert client.cookies.get(cookie_transport.cookie_name) == old_token

        reauthentication_response = await client.post(
            "/auth/session/reauthenticate",
            json={"password": password},
        )
        assert reauthentication_response.status_code == 204
        assert SESSION_IDLE_EXPIRES_HEADER in reauthentication_response.headers
        assert SESSION_ABSOLUTE_EXPIRES_HEADER in reauthentication_response.headers

        new_token = client.cookies.get(cookie_transport.cookie_name)
        assert new_token is not None
        assert new_token != old_token

    tokens = (await user_session.execute(select(AccessToken))).scalars().all()
    assert [token.token for token in tokens] == [new_token]
