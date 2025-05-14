from __future__ import annotations

import io
import os
import tempfile
from typing import Annotated

import pandas as pd
from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from ...import_data.manager.import_manager import ImportManager


def create_router() -> APIRouter:
    router = APIRouter(prefix="/research", tags=["research-admin"])

    @router.post("/import-csv/")
    async def import_csv_data(
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
        """
        # Create temporary files for both CSVs
        temp_additional_file = None
        temp_labels_file = None

        try:
            # Read and validate the additional data CSV
            contents = await additional_data_file.read()
            additional_csv_data = pd.read_csv(
                io.BytesIO(contents),
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )

            manager = ImportManager(debug=True)
            manager.data_manager.validate_additional_import_csv(additional_csv_data)

            # Create a temporary file for additional data
            temp_additional_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".csv", prefix="temp_additional_data_"
            )

            await manager.data_manager.save_additional_import_csv_into_dataframe(
                additional_csv_data, temp_additional_file
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

                # Create a temporary file for labels
                temp_labels_file = tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".csv", prefix="temp_labels_"
                )

                await manager.data_manager.save_labels_csv_into_dataframe(
                    labels_csv_data, temp_labels_file
                )

            # Run the import process
            await manager.run_additional_data_import()

            return {"message": "CSV data imported successfully"}

        except Exception as e:
            print("Error!", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing CSV file: {str(e)}",
            ) from e

        finally:
            # Clean up temporary files
            if temp_additional_file:
                temp_additional_file.close()
                os.unlink(temp_additional_file.name)

            if temp_labels_file:
                temp_labels_file.close()
                os.unlink(temp_labels_file.name)

    return router
