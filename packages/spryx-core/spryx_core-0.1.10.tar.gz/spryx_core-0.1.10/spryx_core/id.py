"""
ID generation and validation utilities.

This module provides functions for generating and validating unique entity IDs.
It uses ULID (Universally Unique Lexicographically Sortable Identifier) as the
primary ID format, with fallback to UUID4 if the ULID library is not available.
"""

from __future__ import annotations

import re
import uuid
from typing import Final, NewType

try:
    import ulid as ulid_lib

    _has_ulid = True
except ImportError:
    _has_ulid = False

# Custom type for entity IDs
EntityId = NewType("EntityId", str)

# Regex for validating ULID format
_ULID_RE: Final = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


def generate_entity_id() -> EntityId:
    """
    Generate a new unique entity ID.

    Returns:
        EntityId: A new ULID as a string (falls back to UUID4 if ULID is not available)
    """
    if _has_ulid:
        # Use ulid package to generate a new ULID
        return EntityId(str(ulid_lib.ULID()))
    return EntityId(str(uuid.uuid4()))


def is_valid_ulid(value: str) -> bool:
    """
    Check if a string is a valid ULID.

    Args:
        value: The string to validate

    Returns:
        bool: True if the string is a valid ULID, False otherwise
    """
    return bool(_ULID_RE.fullmatch(value))


def cast_entity_id(value: str) -> EntityId:
    """
    Cast a string to an EntityId type.

    Args:
        value: The string to cast

    Returns:
        EntityId: The string as an EntityId
    """
    return EntityId(value)
