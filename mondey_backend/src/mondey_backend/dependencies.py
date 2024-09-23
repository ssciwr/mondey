from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .databases.milestones import engine as milestones_engine
from .models.users import User
from .users import fastapi_users


def get_session():
    with Session(milestones_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

current_active_user = fastapi_users.current_user(active=True)

CurrentActiveUserDep = Annotated[User, Depends(current_active_user)]

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)

AdminDep = Depends(current_active_superuser)