# Spryx Core

[![PyPI version](https://img.shields.io/pypi/v/spryx-core.svg)](https://pypi.org/project/spryx-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/spryx-core.svg)](https://pypi.org/project/spryx-core/)
[![Documentation Status](https://github.com/spryx-ai/spryx-core-py/actions/workflows/docs.yml/badge.svg)](https://spryx-ai.github.io/spryx-core-py/)

Core utilities and types for Spryx projects.

## Overview

Spryx Core provides common utilities and type definitions used across Spryx projects, including:

- ID generation and validation using ULIDs
- Time manipulation and formatting utilities
- Pagination models for API responses
- Type definitions and sentinel values
- Common error classes
- Permission handling utilities

## Installation

```bash
pip install spryx-core
```

For development or optional features:

```bash
# For ULID support (recommended for ID generation)
pip install "spryx-core[ulid]"
```

## Documentation

The full documentation is available at [https://spryx-ai.github.io/spryx-core-py/](https://spryx-ai.github.io/spryx-core-py/)

### Local Documentation

You can also build and view the documentation locally:

```bash
# Install documentation dependencies
pip install mkdocs-material "mkdocstrings[python]"

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Quick Usage

```python
from spryx_core import generate_entity_id, now_utc, to_iso, Page

# Generate unique IDs
entity_id = generate_entity_id()
print(entity_id)  # Example: 01HNJG7VWTZA0CGTJ9T7WG9CPB

# Work with UTC timestamps
current_time = now_utc()
iso_timestamp = to_iso(current_time)
print(iso_timestamp)  # Example: 2023-12-01T14:32:15.123456Z

# Create paginated responses
page = Page(
    items=["item1", "item2"],
    page=1,
    page_size=10,
    total=25
)
print(f"Current page: {page.page}, Total pages: {page.total_pages}")
```

## Development

See the [Contributing Guide](https://spryx-ai.github.io/spryx-core-py/development/contributing/) for instructions on how to set up the development environment and contribute to the project.

## License

MIT

## Features

spryx-core provides common utilities and type definitions used across Spryx projects, including:

### Entity IDs

- ULID generation and validation (with UUID fallback)
- Custom `EntityId` type

```python
from spryx_core import EntityId, generate_entity_id, is_valid_ulid

# Generate a new ID
entity_id = generate_entity_id()

# Validate an ID
if is_valid_ulid(some_string):
    # ...
```

### Time Utilities

- ISO-8601 UTC formatting and parsing
- Common time operations (start/end of day, etc.)

```python
from spryx_core import now_utc, to_iso, parse_iso, start_of_day

# Get current UTC time
now = now_utc()

# Format as ISO string
iso_string = to_iso(now)

# Parse ISO string
dt = parse_iso("2023-04-01T12:00:00.000Z")

# Get start of day
day_start = start_of_day(now)
```

### Sentinel Values

- `NotGiven` sentinel and related utilities
- `NOT_GIVEN` singleton instance

```python
from spryx_core import NOT_GIVEN, NotGivenOr, is_given

def my_function(optional_param: NotGivenOr[str] = NOT_GIVEN):
    if is_given(optional_param):
        # Handle provided value
    else:
        # Handle not provided case
```

### Enumerations

- Common enum types (`Environment`, `SortOrder`, etc.)

```python
from spryx_core import Environment, SortOrder

# Environment types
if env == Environment.PRODUCTION:
    # ...

# Sort order
order = SortOrder.ASC
```

## Documentation

### Module: `spryx_core.id`

Functions for generating and validating entity IDs:

- `generate_entity_id() -> EntityId`: Generates a new ULID or UUID
- `is_valid_ulid(value: str) -> bool`: Validates a ULID string
- `cast_entity_id(value: str) -> EntityId`: Casts a string to an EntityId

### Module: `spryx_core.time`

Date/time utilities with UTC focus:

- `now_utc() -> datetime`: Gets current UTC time
- `to_iso(dt: datetime, milliseconds: bool = False) -> str`: Formats as ISO-8601
- `parse_iso(value: str) -> datetime`: Parses ISO-8601 string
- `utc_from_timestamp(ts: int | float) -> datetime`: Converts timestamp to datetime
- `start_of_day(dt: datetime | None = None) -> datetime`: Gets day start (00:00:00)
- `end_of_day(dt: datetime | None = None) -> datetime`: Gets day end (23:59:59.999999)

### Module: `spryx_core.types`

Type utilities:

- `is_given(obj: NotGivenOr[_T]) -> TypeGuard[_T]`: Checks if value is not NotGiven
- `default_or_given(obj: NotGivenOr[_T], default: Any = None) -> Union[_T, None]`: Gets value or default

### Module: `spryx_core.enums`

Common enumerations:

- `SortOrder`: ASC, DESC
- `Environment`: DEV, STAGING, PRODUCTION

### Module: `spryx_core.sentinels`

Sentinel values:

- `NotGiven`: Sentinel for unspecified values, distinct from None

### Module: `spryx_core.constants`

Exported constants:

- `NOT_GIVEN`: Singleton instance of NotGiven

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Requirements

- Python 3.11+
- Dependencies:
  - python-ulid (>=3.0.0,<4.0.0)
  - pydantic (>=2.11.3,<3.0.0)