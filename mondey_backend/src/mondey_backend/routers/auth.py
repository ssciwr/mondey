from __future__ import annotations

from fastapi import APIRouter

from ..models.users import UserCreate
from ..models.users import UserRead
from ..users import auth_backend
from ..users import fastapi_users


def create_router() -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])
    router.include_router(fastapi_users.get_auth_router(auth_backend))
    router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
    router.include_router(fastapi_users.get_reset_password_router())
    router.include_router(fastapi_users.get_verify_router(UserRead))
    return router
