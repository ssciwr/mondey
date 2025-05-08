from __future__ import annotations

import io

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
from ..import_data.align_additional_data_to_current_answers import align_additional_data_to_current_answers
from ..import_data.remove_duplicate_cases import remove_duplicate_cases
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
                encoding_errors="replace"
            )

            print("Read file.")

            # Check for required columns
            required_columns = ["FK05", "CASE"]
            if not all(column in csv_data.columns for column in required_columns):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV must contain the following columns: {', '.join(required_columns)}",
                )

            # Define a path for the CSV file
            csv_file = "temp_uploaded_data.csv"

            # Save the CSV data locally
            try:
                csv_data.to_csv(csv_file, index=False, sep="\t", encoding="utf-16")
                print(f"CSV saved to {csv_file}")

                await remove_duplicate_cases(csv_file, session, csv_file)
                print("Removed duplicates before processing")


                # Process the CSV data
                # todo: This path solution is ugly
                await align_additional_data_to_current_answers(data_path=csv_file,
                                                         labelling_path=
                                                         "src/mondey_backend/import_data/labels_encoded.csv",
                                                         questions_configuration_path=
                                                         "src/mondey_backend/import_data/questions_specified.csv")
                # if it errors, it will go through to the throw 400 error block.
                print("Finished adding additional data")

                return {
                    "status": "success",
                    "message": "CSV data successfully imported",
                }

            finally:
                try:
                    import os

                    if "csv_file" in locals() and os.path.exists(csv_file):
                        os.remove(csv_file)
                        print(f"Cleanup - deleted the temporary CSV file: {csv_file}")
                except Exception as cleanup_error:
                    print(
                        f"Warning: Failed to delete temporary CSV file: {str(cleanup_error)}"
                    )

        except Exception as e:
            print("Error!", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing CSV file: {str(e)}",
            )

    return router
