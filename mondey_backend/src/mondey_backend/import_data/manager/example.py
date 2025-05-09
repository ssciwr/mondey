"""
Example script demonstrating how to use the ImportManager.

This script shows how to perform common import operations using the ImportManager.
"""

import asyncio
import logging

from mondey_backend.import_data.manager import ImportManager


async def run_example():
    """Run an example import using the ImportManager."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create an ImportManager with default settings
    manager = ImportManager(debug=True)

    # Print current paths
    print("Current import paths:")
    print(f"Labels: {manager.import_paths.labels_path}")
    print(f"Data: {manager.import_paths.data_path}")
    print(f"Questions: {manager.import_paths.questions_configured_path}")
    print(f"Milestones: {manager.import_paths.milestones_metadata_path}")
    print(f"Additional data: {manager.import_paths.additional_data_path}")
    print(f"Mondey DB: {manager.mondey_db_path}")
    print(f"Current DB: {manager.current_db_path}")
    print(f"Users DB: {manager.users_db_path}")

    # Example: Load data
    try:
        labels_df = manager.load_labels_df()
        data_df = manager.load_data_df()
        questions_df = manager.load_questions_configured_df()

        print(f"Loaded {len(labels_df)} label rows")
        print(f"Loaded {len(data_df)} data rows")
        print(f"Loaded {len(questions_df)} question rows")
    except Exception as e:
        print(f"Error loading data: {e}")

    # Example: Run a full import
    try:
        print("\nRunning full import...")
        await manager.run_full_import()
        print("Full import completed successfully")
    except Exception as e:
        print(f"Error during full import: {e}")

    # Example: Import additional data
    try:
        print("\nImporting additional data...")
        # Set additional data path if needed
        # manager.import_paths.additional_data_path = Path("path/to/additional_data.csv")
        await manager.run_additional_data_import()
        print("Additional data import completed successfully")
    except Exception as e:
        print(f"Error during additional data import: {e}")


if __name__ == "__main__":
    asyncio.run(run_example())
