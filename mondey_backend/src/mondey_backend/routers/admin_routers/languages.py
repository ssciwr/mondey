from __future__ import annotations

import json
import pathlib

from fastapi import APIRouter
from fastapi import HTTPException

from ...dependencies import SessionDep
from ...models.milestones import Language
from ...settings import app_settings
from ..utils import add
from ..utils import get


def create_router() -> APIRouter:
    router = APIRouter()

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

    return router
