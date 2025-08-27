from __future__ import annotations

from fastapi import APIRouter

from ...dependencies import SessionDep
from ...models.milestones import AdminSettings
from ...models.milestones import AdminSettingsPublic
from ...models.milestones import AdminSettingsUpdate
from ..utils import get


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/settings/", response_model=AdminSettingsPublic)
    def get_admin_settings(session: SessionDep):
        """Get current admin settings."""
        settings = get(session, AdminSettings, 1)
        return settings

    @router.put("/settings/", response_model=AdminSettingsPublic)
    def update_admin_settings(
        session: SessionDep, settings_update: AdminSettingsUpdate
    ):
        """Update admin settings."""
        settings = get(session, AdminSettings, 1)

        update_data = settings_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        session.add(settings)
        session.commit()
        session.refresh(settings)

        return settings

    return router
