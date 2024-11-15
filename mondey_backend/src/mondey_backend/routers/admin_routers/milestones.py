from __future__ import annotations

import pathlib

from fastapi import APIRouter
from fastapi import UploadFile
from sqlmodel import col
from sqlmodel import select

from ...dependencies import SessionDep
from ...models.milestones import Language
from ...models.milestones import Milestone
from ...models.milestones import MilestoneAdmin
from ...models.milestones import MilestoneAgeScores
from ...models.milestones import MilestoneGroup
from ...models.milestones import MilestoneGroupAdmin
from ...models.milestones import MilestoneGroupText
from ...models.milestones import MilestoneImage
from ...models.milestones import MilestoneText
from ...models.utils import ItemOrder
from ...settings import app_settings
from ..utils import add
from ..utils import calculate_milestone_age_scores
from ..utils import get
from ..utils import update_item_orders
from ..utils import update_milestone_group_text
from ..utils import update_milestone_text
from ..utils import write_file


def create_router() -> APIRouter:
    router = APIRouter()

    @router.get("/milestone-groups/", response_model=list[MilestoneGroupAdmin])
    def get_milestone_groups_admin(session: SessionDep):
        milestone_groups = session.exec(
            select(MilestoneGroup).order_by(col(MilestoneGroup.order))
        ).all()
        return milestone_groups

    @router.post("/milestone-groups/", response_model=MilestoneGroupAdmin)
    def create_milestone_group_admin(session: SessionDep):
        db_milestone_group = MilestoneGroup()
        add(session, db_milestone_group)
        for language in session.exec(select(Language)).all():
            session.add(
                MilestoneGroupText(group_id=db_milestone_group.id, lang_id=language.id)
            )
        session.commit()
        session.refresh(db_milestone_group)
        return db_milestone_group

    @router.put("/milestone-groups", response_model=MilestoneGroupAdmin)
    def update_milestone_group_admin(
        session: SessionDep,
        milestone_group: MilestoneGroupAdmin,
    ):
        db_milestone_group = get(session, MilestoneGroup, milestone_group.id)
        for key, value in milestone_group.model_dump(
            exclude={"text", "milestones"}
        ).items():
            setattr(db_milestone_group, key, value)
        update_milestone_group_text(session, milestone_group)
        add(session, db_milestone_group)
        return db_milestone_group

    @router.delete("/milestone-groups/{milestone_group_id}")
    def delete_milestone_group_admin(session: SessionDep, milestone_group_id: int):
        milestone_group = get(session, MilestoneGroup, milestone_group_id)
        session.delete(milestone_group)
        session.commit()
        return {"ok": True}

    @router.post("/milestone-groups/order/")
    def order_milestone_groups_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, MilestoneGroup, item_orders)
        return {"ok": True}

    @router.put("/milestone-group-images/{milestone_group_id}")
    async def upload_milestone_group_image(
        session: SessionDep, milestone_group_id: int, file: UploadFile
    ):
        milestone_group = get(session, MilestoneGroup, milestone_group_id)
        filename = f"{app_settings.STATIC_FILES_PATH}/mg{milestone_group.id}.jpg"
        write_file(file, filename)
        return {"filename": filename}

    @router.post("/milestones/{milestone_group_id}", response_model=MilestoneAdmin)
    def create_milestone(session: SessionDep, milestone_group_id: int):
        db_milestone = Milestone(group_id=milestone_group_id)
        add(session, db_milestone)
        for language in session.exec(select(Language)).all():
            session.add(
                MilestoneText(milestone_id=db_milestone.id, lang_id=language.id)
            )
        session.commit()
        session.refresh(db_milestone)
        return db_milestone

    @router.put("/milestones/", response_model=MilestoneAdmin)
    def update_milestone(
        session: SessionDep,
        milestone: MilestoneAdmin,
    ):
        db_milestone = get(session, Milestone, milestone.id)
        for key, value in milestone.model_dump(exclude={"text", "images"}).items():
            setattr(db_milestone, key, value)
        update_milestone_text(session, milestone)
        add(session, db_milestone)
        return db_milestone

    @router.delete("/milestones/{milestone_id}")
    def delete_milestone(session: SessionDep, milestone_id: int):
        milestone = get(session, Milestone, milestone_id)
        session.delete(milestone)
        session.commit()
        return {"ok": True}

    @router.post("/milestones/order/")
    def order_milestones_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, Milestone, item_orders)
        return {"ok": True}

    @router.post("/milestone-images/{milestone_id}", response_model=MilestoneImage)
    async def upload_milestone_image(
        session: SessionDep, milestone_id: int, file: UploadFile
    ):
        milestone = get(session, Milestone, milestone_id)
        milestone_image = MilestoneImage(milestone_id=milestone.id, approved=True)
        add(session, milestone_image)
        filename = f"m{milestone_image.id}.jpg"
        milestone_image.filename = filename
        write_file(file, f"{app_settings.STATIC_FILES_PATH}/{filename}")
        session.commit()
        session.refresh(milestone_image)
        return milestone_image

    @router.delete("/milestone-images/{milestone_image_id}")
    async def delete_milestone_image(session: SessionDep, milestone_image_id: int):
        milestone_image = get(session, MilestoneImage, milestone_image_id)
        pathlib.Path(
            f"{app_settings.STATIC_FILES_PATH}/m{milestone_image.id}.jpg"
        ).unlink(missing_ok=True)
        session.delete(milestone_image)
        session.commit()
        return {"ok": True}

    @router.get("/milestone-age-scores/{milestone_id}")
    def get_milestone_age_scores(
        session: SessionDep, milestone_id: int
    ) -> MilestoneAgeScores:
        return calculate_milestone_age_scores(session, milestone_id)

    return router