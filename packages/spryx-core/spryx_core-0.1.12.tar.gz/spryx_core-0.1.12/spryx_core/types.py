"""
Type definitions and utilities.

This module provides type utilities for working with optional values and the NotGiven sentinel.
"""

from typing import Any, Type, TypeGuard, TypeVar, Union

from spryx_core.sentinels import NotGiven

_T = TypeVar("_T")

# Union type for values that can be NotGiven
NotGivenOr = Union[_T, Type[NotGiven]]


def is_given(obj: NotGivenOr[_T]) -> TypeGuard[_T]:
    """
    Check if a value is given (not the NotGiven sentinel).

    Args:
        obj: The value to check

    Returns:
        bool: True if the value is not NotGiven, False otherwise
    """
    return obj is not NotGiven


def default_or_given(obj: NotGivenOr[_T], default: Any = None) -> Union[_T, None]:
    """
    Return the given value or a default if NotGiven.

    Args:
        obj: The value to check
        default: The default value to return if obj is NotGiven

    Returns:
        The original value if given, or the default value
    """
    return obj if is_given(obj) else default
