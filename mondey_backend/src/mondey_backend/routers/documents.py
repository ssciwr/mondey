from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.documents import Document
from ..models.documents import DocumentPublic


def create_router() -> APIRouter:
    router = APIRouter(prefix="/documents", tags=["documents"])

    @router.get("/", response_model=list[DocumentPublic])
    def get_public_documents(session: SessionDep):
        documents = session.exec(select(Document)).all()
        return documents

    return router
