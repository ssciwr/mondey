from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import select

from ...dependencies import UserAsyncSessionDep
from ...models.users import User
from ...models.users import UserRead


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/users/", response_model=list[UserRead])
    async def get_users(session: UserAsyncSessionDep):
        users = await session.execute(select(User))
        return users.scalars().all()

    return router
