from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
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

from .databases.users import AccessToken
from .databases.users import User
from .databases.users import get_access_token_db
from .databases.users import get_user_db
from .settings import app_settings


def send_email_validation_link(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = "no-reply@mondey.lkeegan.dev"
    msg["To"] = email
    msg["Subject"] = "MONDEY-Konto aktivieren"
    msg.set_content(
        f"Bitte klicken Sie hier, um Ihr MONDEY-Konto zu aktivieren:\n\nhttps://mondey.lkeegan.dev/verify/{token}"
    )
    with smtplib.SMTP(app_settings.SMTP_HOST) as s:
        s.send_message(msg)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = app_settings.SECRET
    verification_token_secret = app_settings.SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logging.info(f"User {user.email} registered.")
        await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        logging.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )
        send_email_validation_link(user.email, token)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)


cookie_transport = CookieTransport(
    cookie_max_age=3600,
    cookie_secure=app_settings.COOKIE_SECURE,
    cookie_samesite="strict",
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
