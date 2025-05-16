# Import Manager

The Import Manager is a centralized system for handling data import operations in the Mondey backend.

It contains a data_manager which covers just the database/file path/validation of CSV work, to have a clearer separation
of concerns.

*This has been AI generated on the first path as a refactoring of the dispersed function-based import code that existed
before.*


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
