from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from sqlmodel import select

from ...dependencies import CurrentActiveUserDep
from ...dependencies import SessionDep
from ...models.documents import Document
from ...models.documents import DocumentAdmin
from ...models.documents import DocumentCreate
from ..utils import add
from ..utils import document_path
from ..utils import get
from ..utils import write_pdf_file


def create_router() -> APIRouter:
    router = APIRouter(prefix="/admin/documents", tags=["admin", "documents"])

    @router.get("/", response_model=list[DocumentAdmin])
    def get_documents(session: SessionDep):
        documents = session.exec(select(Document)).all()
        return documents

    @router.post("/", response_model=DocumentAdmin)
    def create_document(
        session: SessionDep,
        current_user: CurrentActiveUserDep,
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
    ):
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "File must be a PDF")

        db_document = Document(
            title=title,
            description=description,
            filename=file.filename,
            uploaded_by_user_id=current_user.id,
        )
        add(session, db_document)
        if db_document.id is None:
            raise HTTPException(500, "Failed to create document")
        write_pdf_file(file, document_path(db_document.id))
        return db_document

    @router.put("/{document_id}", response_model=DocumentAdmin)
    def update_document(
        session: SessionDep,
        document_id: int,
        document: DocumentCreate,
    ):
        db_document = get(session, Document, document_id)
        db_document.sqlmodel_update(document.model_dump())
        session.commit()
        return db_document

    @router.delete("/{document_id}")
    def delete_document(
        session: SessionDep,
        document_id: int,
    ):
        db_document = get(session, Document, document_id)
        document_path(document_id).unlink(missing_ok=True)
        session.delete(db_document)
        session.commit()
        return {"ok": True}

    return router
