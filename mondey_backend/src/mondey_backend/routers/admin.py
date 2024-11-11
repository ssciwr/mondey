from __future__ import annotations

import json
import pathlib

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import col
from sqlmodel import select

from ..dependencies import AdminDep
from ..dependencies import SessionDep
from ..models.milestones import Language
from ..models.milestones import Milestone
from ..models.milestones import MilestoneAdmin
from ..models.milestones import MilestoneGroup
from ..models.milestones import MilestoneGroupAdmin
from ..models.milestones import MilestoneGroupText
from ..models.milestones import MilestoneImage
from ..models.milestones import MilestoneText
from ..models.questions import ChildQuestion
from ..models.questions import ChildQuestionAdmin
from ..models.questions import ChildQuestionText
from ..models.questions import UserQuestion
from ..models.questions import UserQuestionAdmin
from ..models.questions import UserQuestionText
from ..settings import app_settings
from .utils import add
from .utils import get
from .utils import update_child_question_text
from .utils import update_milestone_group_text
from .utils import update_milestone_text
from .utils import update_user_question_text
from .utils import write_file


def create_router() -> APIRouter:
    router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[AdminDep])

    @router.post("/languages/", response_model=Language)
    def create_language(session: SessionDep, language: Language):
        db_language = Language.model_validate(language)
        if session.get(Language, db_language.id) is not None:
            raise HTTPException(400, "Language already exists")
        add(session, db_language)
        return db_language

    @router.delete("/languages/{language_id}")
    def delete_language(session: SessionDep, language_id: str):
        if language_id in ["de", "en"]:
            raise HTTPException(
                status_code=400, detail=f"{language_id} language cannot be deleted"
            )
        language = get(session, Language, language_id)
        session.delete(language)
        session.commit()
        return {"ok": True}

    @router.put("/i18n/{language_id}")
    async def update_i18n(
        session: SessionDep, language_id: str, i18dict: dict[str, dict[str, str]]
    ):
        language = get(session, Language, language_id)
        i18json_path = (
            pathlib.Path(app_settings.STATIC_FILES_PATH)
            / "i18n"
            / f"{language.id}.json"
        )
        i18json_path.parent.mkdir(exist_ok=True)
        with open(i18json_path, "w", encoding="utf-8") as i18json_file:
            json.dump(i18dict, i18json_file, separators=(",", ":"), ensure_ascii=False)
        return {"ok": True}

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

    # User question CRUD endpoints
    @router.get("/user-questions/", response_model=list[UserQuestionAdmin])
    def get_user_questions_admin(session: SessionDep):
        user_questions = session.exec(
            select(UserQuestion).order_by(col(UserQuestion.order))
        ).all()
        return user_questions

    @router.post("/user-questions/", response_model=UserQuestionAdmin)
    def create_user_question(session: SessionDep):
        user_question = UserQuestion()
        add(session, user_question)
        for language in session.exec(select(Language)).all():
            session.add(
                UserQuestionText(user_question_id=user_question.id, lang_id=language.id)
            )
        session.commit()
        session.refresh(user_question)
        return user_question

    @router.put("/user-questions/", response_model=UserQuestionAdmin)
    def update_user_question(
        session: SessionDep,
        user_question: UserQuestionAdmin,
    ):
        db_user_question = get(session, UserQuestion, user_question.id)
        for key, value in user_question.model_dump(exclude={"text"}).items():
            setattr(db_user_question, key, value)
        update_user_question_text(session, user_question)
        add(session, db_user_question)
        return db_user_question

    @router.delete("/user-questions/{user_question_id}")
    def delete_user_question(session: SessionDep, user_question_id: int):
        question = get(session, UserQuestion, user_question_id)
        session.delete(question)
        session.commit()
        return {"ok": True}

    # Child question CRUD endpoints
    @router.get("/child-questions/", response_model=list[ChildQuestionAdmin])
    def get_child_questions_admin(session: SessionDep):
        user_questions = session.exec(
            select(ChildQuestion).order_by(col(ChildQuestion.order))
        ).all()
        return user_questions

    @router.post("/child-questions/", response_model=ChildQuestionAdmin)
    def create_child_question(
        session: SessionDep,
    ):
        child_question = ChildQuestion()
        add(session, child_question)
        for language in session.exec(select(Language)).all():
            session.add(
                ChildQuestionText(
                    child_question_id=child_question.id, lang_id=language.id
                )
            )
        session.commit()
        session.refresh(child_question)
        return child_question

    @router.put("/child-questions/", response_model=ChildQuestionAdmin)
    def update_child_question(
        session: SessionDep,
        child_question: ChildQuestionAdmin,
    ):
        db_child_question = get(session, ChildQuestion, child_question.id)

        for key, value in child_question.model_dump(exclude={"text"}).items():
            setattr(db_child_question, key, value)
        update_child_question_text(session, child_question)
        add(session, db_child_question)
        return db_child_question

    @router.delete("/child-questions/{child_question_id}")
    def delete_child_question(session: SessionDep, child_question_id: int):
        question = get(session, ChildQuestion, child_question_id)
        session.delete(question)
        session.commit()
        return {"ok": True}

    return router
