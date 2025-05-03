# pygenutils

**pygenutils** is a comprehensive Python utilities package designed to provide a wide range of general-purpose tools for data manipulation, string handling, time operations, and system interactions. It serves as a collection of commonly needed utilities for Python development.

## Features

- **String Operations**:
  - Advanced string manipulation
  - Text formatting and parsing
  - String pattern matching
  - Text transformation utilities
- **Time Handling**:
  - Date and time calculations
  - Calendar operations
  - Time formatting
  - Program execution timing
  - Countdown functionality
- **Data Structures**:
  - Array and list manipulation
  - Data pattern matching
  - Mathematical operations
  - Data conversion utilities
- **System Operations**:
  - Operating system interactions
  - Process management
  - System information retrieval
- **Audio and Video**:
  - Media file handling
  - Format conversion utilities
- **Number Systems**:
  - Base conversion utilities
  - Number system operations
- **Set Operations**:
  - Interval handling
  - Set manipulation
- **Dictionary Operations**:
  - Dictionary manipulation
  - Key-value operations

---

## Installation Guide

### Dependency Notice

This package has minimal external dependencies and is designed to be lightweight. Most functionality works with Python's standard library.

### Installation Instructions

Install the package using pip:

```bash
pip install pygenutils
```

### Package Updates

To stay up-to-date with the latest version of this package, simply run:

```bash
pip install --upgrade pygenutils
```

---

## Project Structure

The package is organised into several specialised modules:

- **strings/**: String manipulation utilities
  - `string_handler.py`: Core string operations
  - `text_formatters.py`: Text formatting utilities

- **time_handling/**: Time and date operations
  - `date_and_time_utils.py`: Date/time calculations
  - `time_formatters.py`: Time formatting
  - `calendar_utils.py`: Calendar operations
  - `program_snippet_exec_timers.py`: Execution timing
  - `countdown.py`: Countdown functionality

- **arrays_and_lists/**: Data structure operations
  - `data_manipulation.py`: Data handling
  - `patterns.py`: Pattern matching
  - `conversions.py`: Data conversion
  - `maths.py`: Mathematical operations

- **operative_systems/**: System operations
  - System interaction utilities
  - Process management tools

- **audio_and_video/**: Media handling
  - Media file operations
  - Format conversion

- **number_bases/**: Number system operations
  - Base conversion utilities

- **sets_and_intervals/**: Set operations
  - Interval handling
  - Set manipulation

- **dictionaries/**: Dictionary operations
  - Dictionary manipulation tools

For detailed version history and changes, please refer to:

- `CHANGELOG.md`: Comprehensive list of changes for each version
- `VERSIONING.md`: Versioning policy and guidelines

## Usage Examples

### String Operations

```python
from pygenutils.strings import string_handler, text_formatters

# String manipulation
modified_str = string_handler.modify_obj_specs("example.txt", "new")
formatted_text = text_formatters.print_format_string("Hello, {name}!", name="World")
```

### Time Operations

```python
from pygenutils.time_handling import date_and_time_utils, time_formatters

# Date calculations
next_week = date_and_time_utils.add_days_to_date("2024-03-20", 7)
formatted_time = time_formatters.format_time_string("14:30:00", "HH:MM")
```

### Array Operations

```python
from pygenutils.arrays_and_lists import data_manipulation, patterns

# Data manipulation
processed_data = data_manipulation.process_array([1, 2, 3, 4, 5])
matched_pattern = patterns.find_pattern([1, 2, 3, 1, 2, 3], [1, 2, 3])
```

## Best Practices

1. **Module Organisation**:
   - Use appropriate sub-packages for related functionality
   - Keep utility functions focused and single-purpose
   - Document all public functions and classes

2. **Performance Considerations**:
   - Optimise frequently used operations
   - Use appropriate data structures
   - Consider memory usage for large operations

3. **Error Handling**:
   - Implement proper error checking
   - Provide meaningful error messages
   - Handle edge cases appropriately
