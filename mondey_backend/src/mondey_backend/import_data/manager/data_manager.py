"""
DataManager class for handling dataframe loading and database session management.

This keeps the important import/specific/hardcoding logic in import_manager, whilst this deals with
the database, the files needed for import, and for managing the backend calling this to import
a CSV with data, which includes deduplication and managing the lifecycle of the uploaded users
import CSV.

Splitting it this way makes it a lot more readable
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import IO

import pandas as pd
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import Engine
from sqlmodel import Session

from mondey_backend.databases.mondey import engine as mondey_engine
from mondey_backend.import_data.remove_duplicate_cases import remove_duplicate_cases

from ...settings import app_settings

logger = logging.getLogger(__name__)


@dataclass
class ImportPaths:
    """Dataclass to hold all import file paths. Data and milestones_metadata paths are optional."""

    labels_path: Path
    data_path: Path | None = None
    additional_data_path: Path | None = None

    @classmethod
    def from_strings(
        cls,
        labels_path: str,
        data_path: str | None = None,
        additional_data_path: str | None = None,
    ) -> ImportPaths:
        """Create ImportPaths from string paths."""
        return cls(
            labels_path=Path(labels_path),
            data_path=Path(data_path) if data_path else None,
            additional_data_path=Path(additional_data_path)
            if additional_data_path
            else None,
        )

    @classmethod
    def default(cls, base_dir: Path | None = None, **kwargs) -> ImportPaths:
        """Create default ImportPaths with ability to override specific paths."""
        import_dir: Path = Path(app_settings.PRIVATE_FILES_PATH)

        default_paths = {
            "labels_path": import_dir / "labels_encoded.csv",
            "data_path": import_dir / "data.csv",
            "additional_data_path": import_dir / "additional_data.csv",
        }

        # Override defaults with any provided values
        final_paths = {**default_paths, **kwargs}

        return cls(**final_paths)


class DataManager:
    """
    Manager for data loading and database session handling.

    This class handles:
    1. Loading and parsing CSV data
    2. Creating and managing database connections
    """

    def __init__(
        self,
        import_paths: ImportPaths | None = None,
        debug: bool = False,
    ):
        """
        Initialize the DataManager.

        Args:
            import_paths: Paths to import data files
            debug: Enable debug logging
        """
        self.debug = debug
        self._setup_logging()

        # Set up paths
        script_dir = Path(__file__).parent.parent.parent.parent.parent.absolute()
        self.import_paths = import_paths or ImportPaths.default(script_dir)

        self._labels_df: pd.DataFrame | None = None
        self._data_df: pd.DataFrame | None = None
        self._additional_data_df: pd.DataFrame | None = None

    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # -------------------------------------------------------------------------
    # Data Loading Methods
    # -------------------------------------------------------------------------

    def load_labels_df(self, force_reload: bool = False) -> pd.DataFrame:
        """Load the labels DataFrame."""
        if self._labels_df is None or force_reload:
            logger.info(f"Loading labels from {self.import_paths.labels_path}")
            self._labels_df = pd.read_csv(
                self.import_paths.labels_path,
                sep=",",
                encoding="utf-16",
                encoding_errors="replace",
                index_col=None,
            )
        return self._labels_df

    def load_data_df(self, force_reload: bool = False) -> pd.DataFrame | None:
        """Load the data DataFrame."""
        if self._data_df is None or force_reload:
            if self.import_paths.data_path is None:
                logger.debug("Data file path not specified")
                return None

            # Ensure we have a Path object
            data_path = Path(self.import_paths.data_path)
            if not data_path.exists():
                logger.debug(f"Data file not found at: {data_path}")
                return None

            logger.info(f"Loading data from {data_path}")
            self._data_df = pd.read_csv(
                data_path,
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )
        return self._data_df

    def load_additional_data_df(
        self, force_reload: bool = False
    ) -> pd.DataFrame | None:
        """Load the additional data DataFrame."""
        if self._additional_data_df is None or (
            force_reload and self.import_paths.additional_data_path
        ):
            if self.import_paths.additional_data_path is None:
                logger.debug("Additional data file path not specified")
                return None

            # Ensure we have a Path object
            additional_path = Path(self.import_paths.additional_data_path)
            if not additional_path.exists():
                logger.debug(f"Additional data file not found at: {additional_path}")
                return None

            logger.info(f"Loading additional data from {additional_path}")
            self._additional_data_df = pd.read_csv(
                additional_path,
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )
        return self._additional_data_df

    # -------------------------------------------------------------------------
    # Additional Data Import methods
    # -------------------------------------------------------------------------

    def validate_additional_import_csv(self, csv_data: pd.DataFrame) -> None:
        required_columns = ["FK05", "CASE"]
        if not all(column in csv_data.columns for column in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV must contain the following columns: {', '.join(required_columns)}",
            )

    def validate_labels_csv(self, csv_data: pd.DataFrame) -> None:
        """Validate that the labels CSV has required structure."""
        # Add any specific validation for labels CSV if needed
        if csv_data.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Labels CSV cannot be empty",
            )

    async def save_additional_import_csv_into_dataframe(
        self, csv_data: pd.DataFrame, temp_file: IO[bytes]
    ) -> None:
        """Save additional data CSV using a temporary file."""
        # Save the CSV data to the temporary file
        csv_data.to_csv(temp_file.name, index=False, sep="\t", encoding="utf-16")
        logger.debug(f"CSV saved to temporary file {temp_file.name}")

        import_session, _ = self.get_import_session()

        await remove_duplicate_cases(temp_file.name, import_session)
        logger.debug("Removed duplicates before processing")

        self.import_paths.additional_data_path = Path(temp_file.name)
        self.load_additional_data_df(force_reload=True)

    async def save_labels_csv_into_dataframe(
        self, csv_data: pd.DataFrame, temp_file: IO[bytes]
    ) -> None:
        """Save labels CSV using a temporary file."""
        # Save the CSV data to the temporary file
        csv_data.to_csv(temp_file.name, index=False, sep=",", encoding="utf-16")
        logger.debug(f"Labels CSV saved to temporary file {temp_file.name}")

        self.import_paths.labels_path = Path(temp_file.name)
        self.load_labels_df(force_reload=True)

    # -------------------------------------------------------------------------
    # Database Session Methods
    # -------------------------------------------------------------------------

    def get_import_session(self) -> tuple[Session, Engine]:
        with Session(mondey_engine) as session:
            return session, mondey_engine
        # todo: change to just use the normal session in code that currently calls this?
        # no: we'll keep this so in tests we can easily overwrite for the per-test session DB
        # not sure if the tests already hook into the normal get_session call and overwrite it so this is
        # unnecessary though? low priority.
