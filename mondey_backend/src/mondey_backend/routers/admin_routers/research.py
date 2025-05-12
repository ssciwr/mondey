from __future__ import annotations

import io
import random
import string
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
        file: Annotated[UploadFile, File()],
    ):
        # Read the CSV file
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
            ) from e

    return router
