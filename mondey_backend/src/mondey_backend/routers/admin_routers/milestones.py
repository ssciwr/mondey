from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import UploadFile
from sqlmodel import col
from sqlmodel import select

from ...dependencies import SessionDep
from ...dependencies import UserAsyncSessionDep
from ...models.milestones import Language
from ...models.milestones import Milestone
from ...models.milestones import MilestoneAdmin
from ...models.milestones import MilestoneAgeScoreCollection
from ...models.milestones import MilestoneAgeScoreCollectionPublic
from ...models.milestones import MilestoneGroup
from ...models.milestones import MilestoneGroupAdmin
from ...models.milestones import MilestoneGroupText
from ...models.milestones import MilestoneImage
from ...models.milestones import MilestoneText
from ...models.milestones import SubmittedMilestoneImage
from ...models.milestones import SubmittedMilestoneImagePublic
from ...models.utils import DeleteResponse
from ...models.utils import ItemOrder
from ...statistics import async_update_stats
from ..utils import add
from ..utils import count_milestone_answers_for_milestone
from ..utils import get
from ..utils import milestone_group_image_path
from ..utils import milestone_image_path
from ..utils import submitted_milestone_image_path
from ..utils import update_item_orders
from ..utils import update_milestone_group_text
from ..utils import update_milestone_text
from ..utils import write_image_file


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
        db_milestone_group.sqlmodel_update(
            milestone_group.model_dump(exclude={"text", "milestones"})
        )
        update_milestone_group_text(session, milestone_group)
        add(session, db_milestone_group)
        return db_milestone_group

    @router.delete(
        "/milestone-groups/{milestone_group_id}", response_model=DeleteResponse
    )
    def delete_milestone_group_admin(
        session: SessionDep,
        milestone_group_id: int,
        dry_run: bool = Query(
            True,
            description="When true, shows what would be deleted without actually deleting",
        ),
    ):
        milestone_group = get(session, MilestoneGroup, milestone_group_id)
        affected_milestone_answers = 0
        groups_milestone_ids = [
            milestone.id
            for milestone in milestone_group.milestones
            if milestone.id is not None
        ]

        for milestone_id in groups_milestone_ids:
            affected_milestone_answers += count_milestone_answers_for_milestone(
                session, milestone_id
            )

        if not dry_run:
            session.delete(milestone_group)
            session.commit()

        return {
            "ok": True,
            "dry_run": dry_run,
            "children": {
                "affectedMilestones": len(milestone_group.milestones),
                "affectedAnswers": affected_milestone_answers,
            },
        }

    @router.post("/milestone-groups/order/")
    def order_milestone_groups_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, MilestoneGroup, item_orders)
        return {"ok": True}

    @router.put("/milestone-group-images/{milestone_group_id}")
    async def upload_milestone_group_image(
        session: SessionDep, milestone_group_id: int, file: UploadFile
    ):
        get(session, MilestoneGroup, milestone_group_id)
        write_image_file(file, milestone_group_image_path(milestone_group_id))
        return {"ok": True}

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
        db_milestone.sqlmodel_update(milestone.model_dump(exclude={"text", "images"}))
        update_milestone_text(session, milestone)
        add(session, db_milestone)
        return db_milestone

    @router.delete("/milestones/{milestone_id}", response_model=DeleteResponse)
    def delete_milestone(
        session: SessionDep,
        milestone_id: int,
        dry_run: bool = Query(
            True,
            description="When true, shows what would be deleted without actually deleting",
        ),
    ):
        affected_answers = count_milestone_answers_for_milestone(session, milestone_id)
        if not dry_run:
            milestone = get(session, Milestone, milestone_id)
            session.delete(milestone)
            session.commit()
        return {
            "ok": True,
            "dry_run": dry_run,
            "children": {"affectedAnswers": affected_answers},
        }

    @router.post("/milestones/order/")
    def order_milestones_admin(session: SessionDep, item_orders: list[ItemOrder]):
        update_item_orders(session, Milestone, item_orders)
        return {"ok": True}

    @router.post("/milestone-images/{milestone_id}", response_model=MilestoneImage)
    async def upload_milestone_image(
        session: SessionDep, milestone_id: int, file: UploadFile
    ):
        milestone = get(session, Milestone, milestone_id)
        milestone_image = MilestoneImage(milestone_id=milestone.id)
        add(session, milestone_image)
        write_image_file(file, milestone_image_path(milestone_image.id))
        return milestone_image

    @router.delete("/milestone-images/{milestone_image_id}")
    async def delete_milestone_image(session: SessionDep, milestone_image_id: int):
        milestone_image = get(session, MilestoneImage, milestone_image_id)
        milestone_image_path(milestone_image_id).unlink(missing_ok=True)
        session.delete(milestone_image)
        session.commit()
        return {"ok": True}

    @router.get(
        "/submitted-milestone-images/",
        response_model=list[SubmittedMilestoneImagePublic],
    )
    def get_submitted_milestone_images(session: SessionDep):
        submitted_milestone_images = session.exec(select(SubmittedMilestoneImage)).all()
        return submitted_milestone_images

    @router.post("/submitted-milestone-images/approve/{submitted_milestone_image_id}")
    async def approve_submitted_milestone_image(
        session: SessionDep, submitted_milestone_image_id: int
    ):
        submitted_milestone_image = get(
            session, SubmittedMilestoneImage, submitted_milestone_image_id
        )
        milestone_id = submitted_milestone_image.milestone_id
        milestone_image = MilestoneImage(milestone_id=milestone_id)
        session.add(milestone_image)
        session.delete(submitted_milestone_image)
        session.commit()
        submitted_milestone_image_path(submitted_milestone_image_id).rename(
            milestone_image_path(milestone_image.id)
        )
        return {"ok": True}

    @router.delete("/submitted-milestone-images/{submitted_milestone_image_id}")
    async def delete_submitted_milestone_image(
        session: SessionDep, submitted_milestone_image_id: int
    ):
        submitted_milestone_image = get(
            session, SubmittedMilestoneImage, submitted_milestone_image_id
        )
        submitted_milestone_image_path(submitted_milestone_image_id).unlink(
            missing_ok=True
        )
        session.delete(submitted_milestone_image)
        session.commit()
        return {"ok": True}

    @router.get(
        "/milestone-age-scores/{milestone_id}",
        response_model=MilestoneAgeScoreCollectionPublic,
    )
    def get_milestone_age_scores(
        session: SessionDep, milestone_id: int
    ) -> MilestoneAgeScoreCollection:
        collection = get(session, MilestoneAgeScoreCollection, milestone_id)

        if collection is None:
            raise HTTPException(
                404,
                detail='"No milestone age score collection with id: ", milestone_id',
            )
        return collection

    @router.post(
        "/update-stats/{incremental_update}",
        response_model=str,
    )
    async def admin_update_stats(
        session: SessionDep, user_session: UserAsyncSessionDep, incremental_update: bool
    ):
        return await async_update_stats(
            session, user_session, incremental_update=incremental_update
        )

    return router
