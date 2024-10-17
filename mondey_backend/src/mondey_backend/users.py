# TODO: 17th Oct. 2024: remove the artificial verification set again as soon as
# the email verification server has been implemented. See 'README' block @ line 33ff

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi import Request
from fastapi_users import BaseUserManager
from fastapi_users import FastAPIUsers
from fastapi_users import IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users.authentication import CookieTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.future import select

from .databases.users import AccessToken
from .databases.users import User
from .databases.users import get_access_token_db
from .databases.users import get_async_session
from .databases.users import get_user_db
from .settings import app_settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = app_settings.SECRET
    verification_token_secret = app_settings.SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        # README: Sets the verified flag artificially to allow users to work without an
        # actual verification process for now. this can go again as soon as we have an email server for verification.
        async for session in get_async_session():
            # find user in database
            result = await session.execute(select(User).filter(User.id == user.id))
            user_entry = result.scalars().first()

            # set verified artificially and write back
            if user_entry:
                user_entry.is_verified = True
                session.add(user_entry)
                await session.commit()
                await session.refresh(user_entry)

                print("user object: ", user_entry.__dict__)
                print(f"User {user_entry.id} has registered.")
                print(f"User is verified? {user_entry.is_verified}")
        # end README

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_max_age=3600, cookie_secure=app_settings.COOKIE_SECURE
)


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
