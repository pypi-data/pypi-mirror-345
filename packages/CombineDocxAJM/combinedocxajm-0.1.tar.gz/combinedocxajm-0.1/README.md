# Module: CombineDocx.py

This module provides functionality for combining multiple 'docx' files into a single file, particularly focusing on the
`CombineDocx` class.
The primary class and methods include:

## Classes:
- **FileSorter**: Handles sorting of files, particularly by extracting and sorting by numerical suffixes in file names.
  - **Attributes**:
    - `NEGATIVE_INFINITY`: Constant used to represent negative infinity.
    - `directory`: Path to the directory containing files to be sorted.
  - **Methods**:
    - `__init__`: Initializes the `FileSorter` with directory and logger.
    - `_extract_last_number`: Extracts the last number from a file name.
    - `sort_by_last_number`: Sorts files based on their numerical suffixes.

- **CombineDocx**: Combines multiple 'docx' files into a single master file.
  - **Attributes**:
    - `_save_path`: Path where the combined file is saved.
    - `auto_overwrite_combined_file`: Boolean indicating whether to auto-overwrite the combined file.
    - `file_list`: List of files to be combined.
    - `_logger`: Logger instance for logging events.
    - `directory_to_combine`: Directory where the combined file will be saved.
    - `combined_filename`: Name of the combined file.
    - `master_filename`: Path to the master file.
    - `_config`: Configuration object for retrieving settings.
  - **Methods**:
    - `__init__`: Initializes the `CombineDocx` class with necessary attributes.
    - `_get_config_auto_overwrite`: Retrieves the auto-overwrite setting from the configuration.
    - `file_age`: Calculates the age of a file based on its creation or modification time.
    - `save_path`: Property that returns the save path for the combined file.
    - `_are_you_sure`: Static method that asks for confirmation of an action.
    - `combine_all_docx`: Combines all 'docx' files into the master file.

- **CombineSortedDocx**: Extends the functionality of `CombineDocx` to combine files that have been sorted.
  - **Attributes**:
    - `file_list`: List of files to be combined.
    - `_logger`: Logger instance for logging events.
    - `directory_to_combine`: Directory where the combined file will be saved.
  - **Methods**:
    - `__init__`: Initializes the `CombineSortedDocx` class with necessary attributes.

## Usage:
The `CombineDocx` class can be instantiated and used to combine multiple 'docx' files based on user-defined settings
or default configurations. Additional helper methods provide functionality
for handling file properties and user confirmations.

Example:
```python
from CombineDocx import CombineDocx
combiner = CombineDocx(master_filename="master.docx", file_list=["file1.docx", "file2.docx"], directory_to_combine="docs")
combined_file_path = combiner.combine_all_docx()
print(f"Combined file saved at: {combined_file_path}")
```

This example demonstrates how to create an instance of the `CombineDocx` class and use it to combine
multiple 'docx' files into a single master file.