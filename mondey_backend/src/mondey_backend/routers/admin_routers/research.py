from __future__ import annotations

import io
import tempfile
from typing import Annotated

import pandas as pd
from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from ...dependencies import SessionDep
from ...dependencies import UserAsyncSessionDep
from ...import_data.manager.import_manager import ImportManager


def create_router() -> APIRouter:
    router = APIRouter(prefix="/research", tags=["research-admin"])

    @router.post("/import-csv/")
    async def import_csv_data(
        session: SessionDep,
        user_session: UserAsyncSessionDep,
        additional_data_file: Annotated[
            UploadFile, File(description="Additional data CSV file")
        ],
        labels_file: Annotated[UploadFile, File(description="Labels CSV file")] = None,
    ):
        """
        Import CSV data with optional labels file.

        Args:
            additional_data_file: The main data CSV file (required)
            labels_file: Optional labels CSV file

        Returns:
            dict: Message and count of imported children
        """

        try:
            # Read and validate the additional data CSV
            contents = await additional_data_file.read()
            additional_csv_data = pd.read_csv(
                io.BytesIO(contents),
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )

            manager = ImportManager(
                session=session, user_session=user_session, debug=True
            )
            manager.data_manager.validate_additional_import_csv(additional_csv_data)

            # Create temporary files for additional data and labels
            with (
                tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", prefix="temp_additional_data_"
                ) as temp_additional_file,
                tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", prefix="temp_labels_"
                ) as temp_labels_file,
            ):
                await manager.data_manager.save_additional_import_csv_into_dataframe(
                    additional_csv_data, temp_additional_file.name
                )

                # Handle labels file if provided
                if labels_file:
                    labels_contents = await labels_file.read()
                    labels_csv_data = pd.read_csv(
                        io.BytesIO(labels_contents),
                        sep=",",  # Note: using comma separator for labels
                        encoding="utf-16",
                        encoding_errors="replace",
                    )

                    manager.data_manager.validate_labels_csv(labels_csv_data)

                    await manager.data_manager.save_labels_csv_into_dataframe(
                        labels_csv_data, temp_labels_file.name
                    )

                # Run the import process and get the count of imported children
                children_imported = await manager.run_additional_data_import()

                return {
                    "message": "CSV data imported successfully",
                    "children_imported": children_imported,
                }

        except Exception as e:
            print("Error!", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing CSV file: {str(e)}",
            ) from e

    return router
