import pytest

from mondey_backend.models.users import UserCreate
from mondey_backend.models.users import UserRead
from mondey_backend.models.users import UserUpdate
from mondey_backend.users import is_test_account_user


@pytest.fixture
def test_user():
    return UserRead(
        id=1,
        email="123tester@testaccount.com",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        full_data_access=False,
        research_group_id=123451,
        is_verified=True,
    )


@pytest.fixture
def active_user():
    return UserRead(
        id=2,
        email="heidelberguser@uni-heidelberg.de",
        is_active=True,
        is_superuser=False,
        is_researcher=False,
        full_data_access=False,
        research_group_id=123451,
        is_verified=True,
    )


def test_is_test_account(test_user, active_user):
    assert is_test_account_user(test_user)

    assert not is_test_account_user(active_user)

    with pytest.raises(TypeError):
        is_test_account_user(active_user.email)
        # When the email gets (wrongly) directly passed in


def test_public_registration_schema_does_not_accept_research_privileges():
    user_create = UserCreate.model_validate(
        {
            "email": "attacker@example.com",
            "password": "password",
            "research_group_id": 123451,
            "is_researcher": True,
            "full_data_access": True,
        }
    )

    assert not hasattr(user_create, "is_researcher")
    assert not hasattr(user_create, "full_data_access")
    assert user_create.create_update_dict() == {
        "email": "attacker@example.com",
        "password": "password",
        "research_group_id": 123451,
    }


def test_self_update_excludes_admin_managed_research_fields():
    user_update = UserUpdate(
        email="updated@example.com",
        is_researcher=True,
        full_data_access=True,
        research_group_id=123451,
    )

    assert user_update.create_update_dict() == {"email": "updated@example.com"}
    assert user_update.create_update_dict_superuser() == {
        "email": "updated@example.com",
        "is_researcher": True,
        "full_data_access": True,
        "research_group_id": 123451,
    }
