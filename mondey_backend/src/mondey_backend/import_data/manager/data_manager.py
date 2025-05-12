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
import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import Engine
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session

from mondey_backend.databases.mondey import create_mondey_db_and_tables_themselves
from mondey_backend.import_data.remove_duplicate_cases import remove_duplicate_cases

from ...settings import app_settings

logger = logging.getLogger(__name__)


@dataclass
class ImportPaths:
    """Dataclass to hold all import file paths."""

    labels_path: Path
    data_path: Path
    questions_configured_path: Path
    milestones_metadata_path: Path
    additional_data_path: Path | None = None

    @classmethod
    def from_strings(
        cls,
        labels_path: str,
        data_path: str,
        questions_configured_path: str,
        milestones_metadata_path: str,
        additional_data_path: str | None = None,
    ) -> ImportPaths:
        """Create ImportPaths from string paths."""
        return cls(
            labels_path=Path(labels_path),
            data_path=Path(data_path),
            questions_configured_path=Path(questions_configured_path),
            milestones_metadata_path=Path(milestones_metadata_path),
            additional_data_path=Path(additional_data_path)
            if additional_data_path
            else None,
        )

    @classmethod
    def default(cls, base_dir: Path | None = None) -> ImportPaths:
        """Create default ImportPaths."""
        import_dir: Path = Path(app_settings.PRIVATE_FILES_PATH)

        return cls(
            labels_path=import_dir / "labels_encoded.csv",
            data_path=import_dir / "data.csv",
            questions_configured_path=import_dir / "questions_specified.csv",
            milestones_metadata_path=import_dir / "milestones_metadata_(variables).csv",
            additional_data_path=import_dir / "additional_data.csv",
        )


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
        mondey_db_path: Path | None = None,
        current_db_path: Path | None = None,
        users_db_path: Path | None = None,
        debug: bool = False,
    ):
        """
        Initialize the DataManager.

        Args:
            import_paths: Paths to import data files
            mondey_db_path: Path to the Mondey database
            current_db_path: Path to the current database
            users_db_path: Path to the users database
            debug: Enable debug logging
        """
        self.debug = debug
        self._setup_logging()

        # Set up paths
        script_dir = Path(__file__).parent.parent.parent.parent.parent.absolute()
        self.import_paths = import_paths or ImportPaths.default(script_dir)

        # Database paths
        self.current_db_path = current_db_path or (
            script_dir / "src/mondey_backend/import_data/current_db/current_mondey.db"
        )
        self.users_db_path = users_db_path or (
            script_dir / "src/mondey_backend/import_data/current_db/current_users.db"
        )

        # Database connections
        # When we want this to work directly on the live DB, we can change these paths to be the same as the normal ones.
        self.current_db_url = f"sqlite:////{self.current_db_path}"
        self.users_db_url = f"sqlite+aiosqlite:///{self.users_db_path}"

        # Create engines
        self.mondey_engine = create_engine(self.current_db_url)
        self.async_users_engine = create_async_engine(self.users_db_url)

        self._labels_df: pd.DataFrame | None = None
        self._data_df: pd.DataFrame | None = None
        self._questions_configured_df: pd.DataFrame | None = None
        self._milestones_metadata_df: pd.DataFrame | None = None
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

    def load_data_df(self, force_reload: bool = False) -> pd.DataFrame:
        """Load the data DataFrame."""
        if self._data_df is None or force_reload:
            logger.info(f"Loading data from {self.import_paths.data_path}")
            self._data_df = pd.read_csv(
                self.import_paths.data_path,
                sep="\t",
                encoding="utf-16",
                encoding_errors="replace",
            )
        return self._data_df

    def load_questions_configured_df(self, force_reload: bool = False) -> pd.DataFrame:
        """Load the questions configured DataFrame."""
        if self._questions_configured_df is None or force_reload:
            logger.info(
                f"Loading questions configuration from {self.import_paths.questions_configured_path}"
            )
            self._questions_configured_df = pd.read_csv(
                self.import_paths.questions_configured_path,
                sep=",",
                encoding="utf-8",
                dtype=str,
                encoding_errors="replace",
            )
            # Only strip columns if the dataframe was successfully loaded
            self._questions_configured_df.columns = (
                self._questions_configured_df.columns.str.strip()
            )
        return self._questions_configured_df

    def load_milestones_metadata_df(self, force_reload: bool = False) -> pd.DataFrame:
        """Load the milestones metadata DataFrame."""
        if self._milestones_metadata_df is None or force_reload:
            logger.info(
                f"Loading milestones metadata from {self.import_paths.milestones_metadata_path}"
            )
            self._milestones_metadata_df = pd.read_csv(
                self.import_paths.milestones_metadata_path, sep="\t", encoding="utf-16"
            )
        return self._milestones_metadata_df

    def load_additional_data_df(
        self, force_reload: bool = False
    ) -> pd.DataFrame | None:
        """Load the additional data DataFrame."""
        if self._additional_data_df is None or (
            force_reload and self.import_paths.additional_data_path
        ):
            logger.info(
                f"Loading additional data from {self.import_paths.additional_data_path}"
            )
            self._additional_data_df = pd.read_csv(
                self.import_paths.additional_data_path,
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

    async def save_additional_import_csv_into_dataframe(
        self, csv_data: pd.DataFrame, csv_file: str
    ) -> None:  # Define a path for the CSV file
        # Save the CSV data locally
        csv_data.to_csv(csv_file, index=False, sep="\t", encoding="utf-16")
        print(f"CSV saved to {csv_file}")

        import_session, _ = self.get_import_session()

        await remove_duplicate_cases(csv_file, import_session)
        print("Removed duplicates before processing")

        self.import_paths.additional_data_path = Path(csv_file)
        self.load_additional_data_df(force_reload=True)

    def cleanup_additional_data_import(self, csv_file: str) -> None:
        os.remove(csv_file)

    # -------------------------------------------------------------------------
    # Database Session Methods
    # -------------------------------------------------------------------------

    def get_import_session(self, create_tables: bool = False) -> tuple[Session, Engine]:
        """Get a session for the import database."""
        with Session(self.mondey_engine) as session:
            if create_tables:
                create_mondey_db_and_tables_themselves(self.mondey_engine)
            return session, self.mondey_engine

    async def get_async_users_session(self) -> AsyncSession:
        """Get an async session for the users database."""
        async with AsyncSession(self.async_users_engine) as session:
            return session
