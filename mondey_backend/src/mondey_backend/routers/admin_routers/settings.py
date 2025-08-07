from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from sqlmodel import select

from ...dependencies import SessionDep
from ...models.milestones import AdminSettings
from ...models.milestones import AdminSettingsPublic
from ...models.milestones import AdminSettingsUpdate


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/settings/", response_model=AdminSettingsPublic)
    def get_admin_settings(session: SessionDep):
        """Get current admin settings."""
        settings = session.exec(select(AdminSettings)).first()
        if not settings:
            raise HTTPException(500, "Admin settings not found")
        return AdminSettingsPublic.model_validate(settings)

    @router.put("/settings/", response_model=AdminSettingsPublic)
    def update_admin_settings(
        session: SessionDep, settings_update: AdminSettingsUpdate
    ):
        """Update admin settings."""
        settings = session.exec(select(AdminSettings)).first()
        if not settings:
            raise HTTPException(500, "Admin settings not found")

        update_data = settings_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        session.add(settings)
        session.commit()
        session.refresh(settings)

        return AdminSettingsPublic.model_validate(settings)

    return router
