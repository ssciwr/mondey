from __future__ import annotations

import io
import random
import string

import pandas as pd
from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import Response
from fastapi import UploadFile
from fastapi import status
from sqlmodel import select

from ..dependencies import CurrentActiveResearchDep
from ..dependencies import ResearchDep
from ..dependencies import SessionDep
from ..dependencies import UserAsyncSessionDep
from ..import_data.manager.import_manager import ImportManager
from ..models.milestones import Milestone
from ..models.questions import ChildQuestion
from ..models.questions import UserQuestion
from ..statistics import extract_research_data


def create_router() -> APIRouter:
    router = APIRouter(
        prefix="/research", tags=["research"], dependencies=[ResearchDep]
    )

    @router.get("/data/")
    async def get_research_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        current_active_researcher: CurrentActiveResearchDep,
    ):
        if current_active_researcher.full_data_access:
            research_group_id_filter = None
        else:
            research_group_id_filter = current_active_researcher.research_group_id
        df = await extract_research_data(
            session, user_session, research_group_id_filter
        )
        return Response(df.to_json(orient="records"), media_type="application/json")

    @router.get("/names/", response_model=dict[str, dict[int, str]])
    async def get_research_names(session: SessionDep):
        return {
            "milestone": {m.id: m.name for m in session.exec(select(Milestone)).all()},
            "user_question": {
                q.id: q.name for q in session.exec(select(UserQuestion)).all()
            },
            "child_question": {
                q.id: q.name for q in session.exec(select(ChildQuestion)).all()
            },
        }

    @router.post("/import-csv/")
    async def import_csv_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        current_active_researcher: CurrentActiveResearchDep,
        file: UploadFile = File(...),
    ):
        # Check if researcher has full data access
        if not current_active_researcher.full_data_access:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only researchers with full data access can import CSV data",
            )

        # Read the CSV file
        try:
            contents = await file.read()
            csv_data = pd.read_csv(
                io.BytesIO(contents),
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )

            manager = ImportManager(debug=True)
            manager.data_manager.validate_additional_import_csv(csv_data)
            random_string = "".join(random.choices(string.digits, k=10))
            # Create the filename with the random string
            csv_file = f"temp_uploaded_data_{random_string}.csv"
            try:
                await manager.data_manager.save_additional_import_csv_into_dataframe(
                    csv_data, csv_file
                )  # this also cleans it up, deleting it.
                await manager.run_additional_data_import()
            finally:
                manager.data_manager.cleanup_additional_data_import(csv_file)

        except Exception as e:
            print("Error!", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing CSV file: {str(e)}",
            )

    return router
