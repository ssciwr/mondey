from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlmodel import select

from ..dependencies import SessionDep
from ..models.documents import Document
from ..models.documents import DocumentPublic
from .utils import document_path


def create_router() -> APIRouter:
    router = APIRouter(prefix="/documents", tags=["documents"])

    @router.get("/", response_model=list[DocumentPublic])
    def get_public_documents(session: SessionDep):
        documents = session.exec(select(Document)).all()
        return documents

    @router.get("/{document_id}/download", response_class=FileResponse)
    def download_document(session: SessionDep, document_id: int):
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(404, "Document not found")

        file_path = document_path(document_id)
        if not file_path.exists():
            raise HTTPException(404, "Document file not found")

        return FileResponse(
            file_path, media_type="application/pdf", filename=document.filename
        )

    return router
