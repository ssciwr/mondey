from __future__ import annotations

import json

import deepl
from fastapi import APIRouter
from fastapi import HTTPException

from ...dependencies import SessionDep
from ...models.milestones import Language
from ...settings import app_settings
from ..utils import add
from ..utils import get
from ..utils import i18n_language_path


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
        i18json_path = i18n_language_path(language.id)
        i18json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(i18json_path, "w", encoding="utf-8") as i18json_file:
            json.dump(i18dict, i18json_file, separators=(",", ":"), ensure_ascii=False)
        return {"ok": True}

    @router.post("/translate/", response_model=str)
    async def translate(text: str, locale: str, source_lang: str = "de"):
        try:
            deepl_client = deepl.DeepLClient(app_settings.DEEPL_API_KEY)
            if locale == "en":
                # DeepL requires "EN-US" or "EN-GB" instead of "EN", all other languages use the 2-letter code
                locale = "EN-US"
            result = deepl_client.translate_text(
                text,
                target_lang=locale.upper(),
                source_lang=source_lang.upper(),
                formality="prefer_more",
            )
            return result.text
        except Exception as e:
            raise HTTPException(400, str(e)) from e

    return router
