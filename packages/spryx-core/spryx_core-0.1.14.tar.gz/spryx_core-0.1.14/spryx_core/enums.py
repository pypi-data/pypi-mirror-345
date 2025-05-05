"""
Enum definitions used throughout the package.

This module defines enumerations that represent finite sets of values
used across the spryx-core package and dependent projects.
"""

from enum import StrEnum


class SortOrder(StrEnum):
    """
    Sort order options for queries.

    Defines the direction in which results should be sorted.
    """

    ASC = "asc"  # Ascending order (A-Z, 0-9)
    DESC = "desc"  # Descending order (Z-A, 9-0)


class Environment(StrEnum):
    """
    Application environment types.

    Represents the different environments in which an application can run,
    typically used for configuration and behavior differences.
    """

    DEV = "dev"  # Development environment
    STAGING = "staging"  # Staging/testing environment
    PRODUCTION = "production"  # Production environment
