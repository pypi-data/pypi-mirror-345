"""
Sentinel values for special cases.

This module defines sentinel objects that can be used to represent special
cases like "no value provided" in a way that's distinct from None.
"""

from __future__ import annotations

from typing import Literal


class _SentinelBase:
    """
    Base class for sentinel values.

    Sentinel values are used to represent special states that are distinct
    from regular values including None. They always evaluate to False in
    boolean contexts and stringify to their name.
    """

    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        """
        Initialize a sentinel with a name.

        Args:
            name: The name of the sentinel
        """
        self._name = name

    def __bool__(self) -> Literal[False]:
        """
        Sentinels always evaluate to False in boolean contexts.

        Returns:
            False: Always returns False
        """
        return False

    def __repr__(self) -> str:
        """
        String representation of the sentinel.

        Returns:
            str: The name of the sentinel
        """
        return self._name

    def __reduce__(self):
        """
        Support for pickling sentinel instances.

        Returns:
            tuple: Class and constructor arguments
        """
        return (self.__class__, (self._name,))


# Sentinel for indicating that a value was not provided
NotGiven = _SentinelBase("NotGiven")
