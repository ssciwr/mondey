from __future__ import annotations

import datetime
import smtplib
from email.message import EmailMessage
from typing import Annotated

from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi_users import BaseUserManager
from fastapi_users import FastAPIUsers
from fastapi_users import IntegerIDMixin
from fastapi_users import exceptions
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
from .logging import logger
from .models.research import ResearchGroup
from .models.users import SessionInfo
from .settings import app_settings


def send_email(msg: EmailMessage) -> None:
    try:
        if app_settings.SMTP_HOST != "":
            with smtplib.SMTP(app_settings.SMTP_HOST) as s:
                if app_settings.SMTP_USERNAME != "":
                    s.login(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
                s.send_message(msg)
        else:
            logger.warning(f"Email {msg} not sent as SMTP_HOST is not set")
    except smtplib.SMTPException as e:
        logger.error(f"Email {msg} not sent due to SMTP error: {e}")
        logger.exception(e)


def send_email_validation_link(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = f"no-reply@{app_settings.MONDEY_HOST}"
    msg["To"] = email
    msg["Subject"] = "MONDEY-Konto aktivieren"
    msg.set_content(
        f"Bitte klicken Sie hier, um Ihr MONDEY-Konto zu aktivieren:\n\nhttps://{app_settings.MONDEY_HOST}/verify/{token}\n\n-----\n\nPlease click here to activate your MONDEY account:\n\nhttps://{app_settings.MONDEY_HOST}/verify/{token}"
    )
    send_email(msg)


def send_reset_password_link(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = f"no-reply@{app_settings.MONDEY_HOST}"
    msg["To"] = email
    msg["Subject"] = "MONDEY Passwort zurücksetzen"
    msg.set_content(
        f"Bitte klicken Sie hier, um Ihr MONDEY Passwort zurückzusetzen:\n\nhttps://{app_settings.MONDEY_HOST}/resetPassword/{token}\n\n-----\n\nPlease click here to reset your MONDEY password:\n\nhttps://{app_settings.MONDEY_HOST}/resetPassword/{token}"
    )
    send_email(msg)


def is_test_account_user(user: User) -> bool:
    # A bit over-explicit but I wanted to implement the use of pytest.raises and it could help prevent an annoying bug.
    if type(user) is str:
        raise TypeError("Pass in the User object, not their email directly")
    if not hasattr(user, "email"):
        return False
    return "tester@testaccount.com" in user.email


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = app_settings.SECRET
    verification_token_secret = app_settings.SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info(f"User {user.email} registered.")
        if is_test_account_user(user):
            async with async_session_maker() as user_session:
                logger.warning(f"Updating test user to verified {user.email}")
                user_db = await user_session.get(User, user.id)
                if user_db is not None:
                    user_db.is_verified = True
                await user_session.commit()
        with Session(mondey_engine) as mondey_session:
            if mondey_session.get(ResearchGroup, user.research_group_id) is None:
                logger.warning(
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
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")
        send_reset_password_link(user.email, token)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        if is_test_account_user(user):
            return
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )
        send_email_validation_link(user.email, token)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)


SESSION_IDLE_EXPIRES_HEADER = "X-Session-Idle-Expires-At"
SESSION_ABSOLUTE_EXPIRES_HEADER = "X-Session-Absolute-Expires-At"
SESSION_WARNING_SECONDS_HEADER = "X-Session-Warning-Seconds"


def _as_utc(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.UTC)
    return value.astimezone(datetime.UTC)


class SessionDatabaseStrategy(DatabaseStrategy[User, int, AccessToken]):
    def __init__(
        self,
        database: AccessTokenDatabase[AccessToken],
        response: Response | None = None,
    ):
        super().__init__(database)
        self.response = response

    @property
    def touch_interval_seconds(self) -> int:
        return min(
            app_settings.SESSION_TOUCH_INTERVAL_SECONDS,
            max(1, app_settings.SESSION_IDLE_TIMEOUT_SECONDS // 2),
        )

    @property
    def warning_seconds(self) -> int:
        return min(
            app_settings.SESSION_WARNING_SECONDS,
            max(1, app_settings.SESSION_IDLE_TIMEOUT_SECONDS // 2),
        )

    def session_info(self, access_token: AccessToken) -> SessionInfo:
        created_at = _as_utc(access_token.created_at)
        last_seen_at = _as_utc(access_token.last_seen_at)
        return SessionInfo(
            idle_expires_at=last_seen_at
            + datetime.timedelta(seconds=app_settings.SESSION_IDLE_TIMEOUT_SECONDS),
            absolute_expires_at=created_at
            + datetime.timedelta(seconds=app_settings.SESSION_ABSOLUTE_TIMEOUT_SECONDS),
            warning_seconds=self.warning_seconds,
        )

    def set_session_headers(
        self, session_info: SessionInfo, response: Response | None = None
    ) -> None:
        target_response = response if response is not None else self.response
        if target_response is None:
            return
        target_response.headers[SESSION_IDLE_EXPIRES_HEADER] = (
            session_info.idle_expires_at.isoformat()
        )
        target_response.headers[SESSION_ABSOLUTE_EXPIRES_HEADER] = (
            session_info.absolute_expires_at.isoformat()
        )
        target_response.headers[SESSION_WARNING_SECONDS_HEADER] = str(
            session_info.warning_seconds
        )

    async def get_valid_access_token(
        self, token: str | None, *, touch: bool = True
    ) -> AccessToken | None:
        if token is None:
            return None
        access_token = await self.database.get_by_token(token)
        if access_token is None:
            return None

        now = datetime.datetime.now(datetime.UTC)
        created_at = _as_utc(access_token.created_at)
        last_seen_at = _as_utc(access_token.last_seen_at)
        absolute_expired = now >= created_at + datetime.timedelta(
            seconds=app_settings.SESSION_ABSOLUTE_TIMEOUT_SECONDS
        )
        idle_expired = now >= last_seen_at + datetime.timedelta(
            seconds=app_settings.SESSION_IDLE_TIMEOUT_SECONDS
        )
        if absolute_expired or idle_expired:
            await self.database.delete(access_token)
            return None

        if touch and now >= last_seen_at + datetime.timedelta(
            seconds=self.touch_interval_seconds
        ):
            access_token = await self.database.update(
                access_token, {"last_seen_at": now}
            )

        self.set_session_headers(self.session_info(access_token))
        return access_token

    async def read_token(
        self, token: str | None, user_manager: BaseUserManager[User, int]
    ) -> User | None:
        access_token = await self.get_valid_access_token(token)
        if access_token is None:
            return None
        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def rotate_session(
        self, token: str | None, user: User
    ) -> tuple[str, SessionInfo] | None:
        old_access_token = await self.get_valid_access_token(token, touch=False)
        if old_access_token is None:
            return None

        new_access_token = await self.database.create(
            self._create_access_token_dict(user)
        )
        await self.database.delete(old_access_token)
        return new_access_token.token, self.session_info(new_access_token)


cookie_transport = CookieTransport(
    cookie_max_age=app_settings.SESSION_ABSOLUTE_TIMEOUT_SECONDS,
    cookie_secure=app_settings.COOKIE_SECURE,
)


def get_database_strategy(
    response: Response,
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> SessionDatabaseStrategy:
    return SessionDatabaseStrategy(access_token_db, response)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
