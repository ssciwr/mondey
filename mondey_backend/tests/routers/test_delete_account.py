from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI
from fastapi_users.password import PasswordHelper
from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from mondey_backend.models.children import Child
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.users import AccessToken
from mondey_backend.models.users import User
from mondey_backend.routers.utils import child_image_path

PASSWORD = "correct horse battery staple"
# the user fixture with children and answers in the test database
USER_ID = 3


async def _set_password(user_session: AsyncSession, user_id: int) -> User:
    user = await user_session.get(User, user_id)
    assert user is not None
    user.hashed_password = PasswordHelper().hash(PASSWORD)
    await user_session.commit()
    return user


def _users_mondey_data(session: Session, user_id: int) -> dict[str, int]:
    child_ids = session.exec(
        select(Child.id).where(col(Child.user_id) == user_id)
    ).all()
    return {
        "children": len(child_ids),
        "answer_sessions": len(
            session.exec(
                select(MilestoneAnswerSession).where(
                    col(MilestoneAnswerSession.user_id) == user_id
                )
            ).all()
        ),
        "milestone_answers": len(
            session.exec(
                select(MilestoneAnswer)
                .join(MilestoneAnswerSession)
                .where(col(MilestoneAnswerSession.user_id) == user_id)
            ).all()
        ),
        "child_answers": len(
            session.exec(
                select(ChildAnswer).where(col(ChildAnswer.child_id).in_(child_ids))
            ).all()
        ),
        "user_answers": len(
            session.exec(
                select(UserAnswer).where(col(UserAnswer.user_id) == user_id)
            ).all()
        ),
    }


@pytest.mark.asyncio
async def test_delete_account_dry_run_deletes_nothing(
    app: FastAPI, user_session: AsyncSession, session: Session
):
    user = await _set_password(user_session, USER_ID)
    before = _users_mondey_data(session, USER_ID)
    assert before["children"] > 0

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://testserver"
    ) as client:
        assert (
            await client.post(
                "/auth/login", data={"username": user.email, "password": PASSWORD}
            )
        ).status_code == 204
        response = await client.request(
            "DELETE", "/users/me/account", json={"password": PASSWORD}
        )

    assert response.status_code == 200
    assert response.json()["dry_run"] is True
    assert response.json()["children"]["affectedChildren"] == before["children"]
    session.expire_all()
    assert _users_mondey_data(session, USER_ID) == before
    assert await user_session.get(User, USER_ID) is not None


@pytest.mark.asyncio
async def test_delete_account_requires_correct_password(
    app: FastAPI, user_session: AsyncSession, session: Session
):
    user = await _set_password(user_session, USER_ID)
    before = _users_mondey_data(session, USER_ID)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://testserver"
    ) as client:
        assert (
            await client.post(
                "/auth/login", data={"username": user.email, "password": PASSWORD}
            )
        ).status_code == 204
        response = await client.request(
            "DELETE",
            "/users/me/account?dry_run=false",
            json={"password": "wrong password"},
        )

    assert response.status_code == 400
    session.expire_all()
    assert _users_mondey_data(session, USER_ID) == before
    assert await user_session.get(User, USER_ID) is not None


@pytest.mark.asyncio
async def test_delete_account_deletes_user_and_all_their_data(
    app: FastAPI, user_session: AsyncSession, session: Session, private_dir
):
    user = await _set_password(user_session, USER_ID)
    before = _users_mondey_data(session, USER_ID)
    assert before["children"] > 0
    assert before["answer_sessions"] > 0
    assert before["milestone_answers"] > 0
    child_ids = session.exec(
        select(Child.id).where(col(Child.user_id) == USER_ID)
    ).all()
    for child_id in child_ids:
        child_image_path(child_id).parent.mkdir(parents=True, exist_ok=True)
        child_image_path(child_id).write_bytes(b"not really an image")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://testserver"
    ) as client:
        assert (
            await client.post(
                "/auth/login", data={"username": user.email, "password": PASSWORD}
            )
        ).status_code == 204
        response = await client.request(
            "DELETE", "/users/me/account?dry_run=false", json={"password": PASSWORD}
        )

    assert response.status_code == 200
    assert response.json()["dry_run"] is False

    # no data is left behind in the mondey database
    session.expire_all()
    assert _users_mondey_data(session, USER_ID) == {
        "children": 0,
        "answer_sessions": 0,
        "milestone_answers": 0,
        "child_answers": 0,
        "user_answers": 0,
    }
    for child_id in child_ids:
        assert not child_image_path(child_id).is_file()

    # and the account itself is gone from the users database, along with its sessions
    assert await user_session.get(User, USER_ID) is None
    tokens = (await user_session.execute(sa_select(AccessToken))).scalars().all()
    assert [token for token in tokens if token.user_id == USER_ID] == []


@pytest.mark.asyncio
async def test_delete_account_leaves_other_users_data_alone(
    app: FastAPI, user_session: AsyncSession, session: Session
):
    user = await _set_password(user_session, USER_ID)
    other_user_id = 1
    before_other = _users_mondey_data(session, other_user_id)
    assert before_other["children"] > 0

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://testserver"
    ) as client:
        assert (
            await client.post(
                "/auth/login", data={"username": user.email, "password": PASSWORD}
            )
        ).status_code == 204
        response = await client.request(
            "DELETE", "/users/me/account?dry_run=false", json={"password": PASSWORD}
        )

    assert response.status_code == 200
    session.expire_all()
    assert _users_mondey_data(session, other_user_id) == before_other


def test_delete_account_requires_authentication(public_client):
    response = public_client.request(
        "DELETE", "/users/me/account?dry_run=false", json={"password": PASSWORD}
    )
    assert response.status_code == 401
