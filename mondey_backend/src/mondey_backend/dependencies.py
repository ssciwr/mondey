from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session

from .databases.mondey import engine as mondey_engine
from .databases.users import get_async_session
from .models.users import User
from .users import fastapi_users


def get_session():
    with Session(mondey_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

current_active_user = fastapi_users.current_user(active=True)

CurrentActiveUserDep = Annotated[User, Depends(current_active_user)]

UserAsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def current_active_researcher(
    user: Annotated[User, Depends(current_active_user)],
) -> User:
    if user and user.is_researcher:
        return user
    raise HTTPException(401)


ResearchDep = Depends(current_active_researcher)

CurrentActiveResearchDep = Annotated[User, Depends(current_active_user)]

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)

AdminDep = Depends(current_active_superuser)
