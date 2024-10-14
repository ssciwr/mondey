from __future__ import annotations

from fastapi import APIRouter

from ..models.users import UserRead
from ..models.users import UserUpdate
from ..users import fastapi_users


def create_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

    return router
