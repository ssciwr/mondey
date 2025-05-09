# Import Manager

The Import Manager is a centralized system for handling data import operations in the Mondey backend.

*This has been AI generated on the first path as a refactoring of the dispersed function-based import code that existed
before.*

## Overview

This module provides a more maintainable and cohesive approach to importing data, replacing the previous system that was spread across multiple scripts. It handles:

1. Loading and parsing CSV data
2. Creating and managing database connections
3. Importing milestones metadata
4. Importing children with milestone data
5. Importing question/answer data
6. Aligning additional data with existing data

## Usage

### Command Line Interface

The Import Manager provides a command-line interface for running import operations:

```bash
# Run a full import
python -m mondey_backend.import_data.manager.cli full-import

# Import additional data
python -m mondey_backend.import_data.manager.cli additional-import --additional-data path/to/additional_data.csv

# Clear users database
python -m mondey_backend.import_data.manager.cli clear-users
```

### Programmatic Usage

```python
import asyncio
from mondey_backend.import_data.manager import ImportManager

# Create an ImportManager with default settings
manager = ImportManager()

# Run a full import
asyncio.run(manager.run_full_import())

# Import additional data
manager.import_paths.additional_data_path = "path/to/additional_data.csv"
asyncio.run(manager.run_additional_data_import())

# Clear users database
asyncio.run(manager.clear_users_database())
```

## Configuration

The Import Manager can be configured with custom paths for data files and databases:

```python
from pathlib import Path
from mondey_backend.import_data.manager import ImportManager
from mondey_backend.import_data.manager.import_manager import ImportPaths

# Create custom import paths
import_paths = ImportPaths(
    labels_path=Path("path/to/labels.csv"),
    data_path=Path("path/to/data.csv"),
    questions_configured_path=Path("path/to/questions.csv"),
    milestones_metadata_path=Path("path/to/milestones.csv"),
    additional_data_path=Path("path/to/additional_data.csv")
)

# Create ImportManager with custom paths
manager = ImportManager(
    import_paths=import_paths,
    mondey_db_path=Path("path/to/mondey.db"),
    current_db_path=Path("path/to/current.db"),
    users_db_path=Path("path/to/users.db"),
    debug=True
)
```

## Benefits Over Previous Implementation

1. **Centralized Management**: All import functionality is now managed through a single class.
2. **Improved Error Handling**: Better logging and error handling throughout the import process.
3. **Dependency Injection**: Database sessions are passed to methods rather than created within them.
4. **Data Flow**: DataFrames are passed between methods instead of file paths.
5. **Configuration**: Flexible configuration options for paths and settings.
6. **CLI Interface**: Easy-to-use command-line interface for running import operations.
7. **Hardcoded Mappings**: All hardcoded mappings and special case handling are centralized in the ImportManager class.

## Hardcoded Mappings

The ImportManager includes several hardcoded mappings that were previously spread across multiple files:

- Question ID mappings (`hardcoded_id_map`)
- Other answer mappings (`hardcoded_other_answers`)
- Child and user variable lists (`relevant_child_variables`, `relevant_user_variables`)
- Special case handling for:
  - Child age questions
  - Eltern (parent) questions
  - Fruhgeboren/Termingeboren (premature birth) questions
  - Sibling questions

These mappings are used during the import process to correctly map variables to questions and handle special cases.
