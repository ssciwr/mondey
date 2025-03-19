import pytest

from mondey_backend.models.users import UserRead
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
        assert not is_test_account_user(
            active_user.email
        )  # When the email gets (wrongly) directly passed in

    with pytest.raises(TypeError):
        assert not is_test_account_user()  # When no email is present
