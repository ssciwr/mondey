from __future__ import annotations

from random import randint

from checkdigit import verhoeff
from fastapi import APIRouter
from fastapi import HTTPException
from sqlmodel import select

from ...dependencies import SessionDep
from ...dependencies import UserAsyncSessionDep
from ...models.research import ResearchGroup
from ...models.users import User
from ...models.users import UserRead
from ..utils import add
from ..utils import get


def generate_research_group_id() -> int:
    """Generate a possible 6-digit integer research group ID with a checksum."""
    code = randint(10000, 99999)
    checksum = int(verhoeff.calculate(str(code)))
    return code * 10 + checksum


def generate_research_group(session: SessionDep) -> ResearchGroup:
    research_group_id = generate_research_group_id()
    while session.get(ResearchGroup, research_group_id) is not None:
        research_group_id = generate_research_group_id()
    research_group = ResearchGroup(id=research_group_id)
    add(session, research_group)
    return research_group


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/users/", response_model=list[UserRead])
    async def get_users(user_session: UserAsyncSessionDep):
        users = await user_session.execute(select(User))
        return users.scalars().all()

    @router.get("/research-groups/", response_model=list[ResearchGroup])
    async def get_research_groups(session: SessionDep):
        research_groups = session.exec(select(ResearchGroup)).all()
        return research_groups

    @router.post("/research-groups/{user_id}", response_model=ResearchGroup)
    async def create_research_group(
        user_session: UserAsyncSessionDep, session: SessionDep, user_id: int
    ):
        user = await user_session.get(User, user_id)
        if user is None:
            raise HTTPException(404)
        research_group = generate_research_group(session)
        user.is_researcher = True
        user.research_group_id = research_group.id
        user_session.add(user)
        await user_session.commit()
        return research_group

    @router.delete("/research-groups/{research_group_id}")
    async def delete_research_group(session: SessionDep, research_group_id: int):
        research_group = get(session, ResearchGroup, research_group_id)
        session.delete(research_group)
        session.commit()
        return {"ok": True}

    return router
