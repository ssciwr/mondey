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
from sqlmodel import Session

from .databases.mondey import engine as mondey_engine
from .databases.users import AccessToken
from .databases.users import User
from .databases.users import async_session_maker
from .databases.users import get_access_token_db
from .databases.users import get_user_db
from .models.research import ResearchGroup
from .settings import app_settings


def send_email_validation_link(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = "no-reply@mondey.lkeegan.dev"
    msg["To"] = email
    msg["Subject"] = "MONDEY-Konto aktivieren"
    msg.set_content(
        f"Bitte klicken Sie hier, um Ihr MONDEY-Konto zu aktivieren:\n\nhttps://mondey.lkeegan.dev/verify/{token}\n\n-----\n\nPlease click here to activate your MONDEY account:\n\nhttps://mondey.lkeegan.dev/verify/{token}"
    )
    with smtplib.SMTP(app_settings.SMTP_HOST) as s:
        s.send_message(msg)


def send_reset_password_link(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = "no-reply@mondey.lkeegan.dev"
    msg["To"] = email
    msg["Subject"] = "MONDEY Passwort zurücksetzen"
    msg.set_content(
        f"Bitte klicken Sie hier, um Ihr MONDEY Passwort zurückzusetzen:\n\nhttps://mondey.lkeegan.dev/resetPassword/{token}\n\n-----\n\nPlease click here to reset your MONDEY password:\n\nhttps://mondey.lkeegan.dev/resetPassword/{token}"
    )
    with smtplib.SMTP(app_settings.SMTP_HOST) as s:
        s.send_message(msg)


def is_test_account_user(user: User) -> bool:
    if not hasattr(user, 'email'):
        return False
    return 'tester@testaccount.com' in user.email


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = app_settings.SECRET
    verification_token_secret = app_settings.SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logging.info(f"User {user.email} registered.")
        if is_test_account_user(user):
            async with async_session_maker() as user_session:
                logging.warning(
                    f"Updating test user to verified {user.email}"
                )
                user_db = await user_session.get(User, user.id)
                if user_db is not None:
                    user_db.is_verified = True
                await user_session.commit()
        with Session(mondey_engine) as mondey_session:
            if mondey_session.get(ResearchGroup, user.research_group_id) is None:
                logging.warning(
                    f"Invalid research code {user.research_group_id} used by User {user.email} - ignoring."
                )
                async with async_session_maker() as user_session:
                    user_db = await user_session.get(User, user.id)
                    if user_db is not None:
                        user_db.research_group_id = 0
                    await user_session.commit()
        await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        logging.info(f"User {user.id} has forgot their password. Reset token: {token}")
        send_reset_password_link(user.email, token)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        if is_test_account_user(user):
            return
        logging.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )
        send_email_validation_link(user.email, token)


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
