from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from ..dependencies import CurrentActiveUserDep
from ..logging import logger
from ..models.users import SessionReauthentication
from ..models.users import UserCreate
from ..models.users import UserRead
from ..users import SessionDatabaseStrategy
from ..users import UserManager
from ..users import auth_backend
from ..users import cookie_transport
from ..users import fastapi_users
from ..users import get_database_strategy
from ..users import get_user_manager


def create_router() -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])
    router.include_router(fastapi_users.get_auth_router(auth_backend))
    router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
    router.include_router(fastapi_users.get_reset_password_router())
    router.include_router(fastapi_users.get_verify_router(UserRead))

    @router.post("/session/reauthenticate", status_code=204)
    async def reauthenticate_session(
        body: SessionReauthentication,
        request: Request,
        current_active_user: CurrentActiveUserDep,
        strategy: Annotated[SessionDatabaseStrategy, Depends(get_database_strategy)],
        user_manager: Annotated[UserManager, Depends(get_user_manager)],
    ):
        user = await user_manager.get(current_active_user.id)
        verified, updated_password_hash = (
            user_manager.password_helper.verify_and_update(
                body.password.get_secret_value(), user.hashed_password
            )
        )
        if not verified:
            logger.warning(
                "Failed session reauthentication for user %s",
                current_active_user.id,
            )
            raise HTTPException(400, "LOGIN_BAD_CREDENTIALS")
        if updated_password_hash is not None:
            user = await user_manager.user_db.update(
                user, {"hashed_password": updated_password_hash}
            )

        rotated_session = await strategy.rotate_session(
            request.cookies.get(cookie_transport.cookie_name), user
        )
        if rotated_session is None:
            raise HTTPException(401, "Session has expired")
        token, session_info = rotated_session
        response = await cookie_transport.get_login_response(token)
        strategy.set_session_headers(session_info, response)
        logger.info("Session reauthenticated for user %s", user.id)
        return response

    return router
