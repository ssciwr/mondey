import pytest
from checkdigit import verhoeff
from fastapi.testclient import TestClient
from fastapi_users.db import SQLAlchemyUserDatabase

from mondey_backend.models.users import User
from mondey_backend.models.users import UserUpdate
from mondey_backend.users import UserManager


def test_users(admin_client: TestClient):
    response = admin_client.get("/admin/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 5
    assert users[0]["id"] == 1
    assert users[0]["is_researcher"]
    assert users[0]["is_superuser"]
    assert users[1]["id"] == 2
    assert users[1]["is_researcher"]
    assert not users[1]["is_superuser"]
    assert users[2]["id"] == 3
    assert not users[2]["is_researcher"]
    assert not users[2]["is_superuser"]
    assert users[3]["id"] == 4
    assert not users[3]["is_researcher"]
    assert not users[3]["is_superuser"]
    assert users[4]["id"] == 5
    assert "tester@testaccount.com" in users[4]["email"]
    assert not users[4]["is_researcher"]
    assert not users[4]["is_superuser"]


def test_get_research_groups(admin_client: TestClient):
    response = admin_client.get("/admin/research-groups/")
    assert response.status_code == 200
    research_groups = response.json()
    assert research_groups == [{"id": 123451}]


def test_delete_research_group(admin_client: TestClient):
    response = admin_client.delete("/admin/research-groups/123451")
    assert response.status_code == 200
    assert admin_client.get("/admin/research-groups/").json() == []


def test_create_research_group(admin_client: TestClient):
    research_group = {"id": 123451}
    assert admin_client.get("/admin/research-groups/").json() == [research_group]
    users = admin_client.get("/admin/users/").json()
    ordinary_user = next(user for user in users if user["id"] == 4)
    assert not ordinary_user["is_researcher"]
    assert ordinary_user["research_group_id"] == 0

    response = admin_client.post("/admin/research-groups/4")
    assert response.status_code == 200
    new_research_group = response.json()
    assert verhoeff.validate(str(new_research_group["id"]))
    new_groups = admin_client.get("/admin/research-groups/").json()
    assert len(new_groups) == 2
    assert research_group in new_groups
    assert new_research_group in new_groups

    users = admin_client.get("/admin/users/").json()
    updated_user = next(user for user in users if user["id"] == 4)
    assert updated_user["is_researcher"]
    assert updated_user["research_group_id"] == new_research_group["id"]


@pytest.mark.asyncio
async def test_admin_update_persists_research_permissions(user_session):
    user = await user_session.get(User, 4)
    assert user is not None
    assert not user.is_researcher
    assert not user.full_data_access
    assert user.research_group_id == 0

    user_manager = UserManager(SQLAlchemyUserDatabase(user_session, User))
    await user_manager.update(
        UserUpdate(
            is_researcher=True,
            full_data_access=True,
            research_group_id=123451,
        ),
        user,
        safe=False,
    )

    await user_session.refresh(user)
    assert user.is_researcher
    assert user.full_data_access
    assert user.research_group_id == 123451


@pytest.mark.asyncio
async def test_self_update_cannot_persist_research_permissions(user_session):
    user = await user_session.get(User, 4)
    assert user is not None

    user_manager = UserManager(SQLAlchemyUserDatabase(user_session, User))
    await user_manager.update(
        UserUpdate(
            is_researcher=True,
            full_data_access=True,
            research_group_id=123451,
        ),
        user,
        safe=True,
    )

    await user_session.refresh(user)
    assert not user.is_researcher
    assert not user.full_data_access
    assert user.research_group_id == 0
