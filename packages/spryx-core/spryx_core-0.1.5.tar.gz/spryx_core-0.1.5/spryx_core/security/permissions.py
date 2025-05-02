"""
Permission definitions for Spryx applications.

This module defines standardized permission strings in a consistent format
(resource:action) that can be used for role-based access control.
"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import List, Set


@unique
class Permission(StrEnum):
    """Standard permission strings for Spryx applications.

    Permissions follow the format `resource:action` where:
    - resource: The entity being accessed (users, orders, etc.)
    - action: The operation being performed (read, write, etc.)
    """

    # User permissions
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"

    # Order permissions
    READ_ORDERS = "orders:read"
    WRITE_ORDERS = "orders:write"

    # Add more permissions as needed

    @classmethod
    def has_permission(
        cls,
        user_permissions: List[Permission] | Set[Permission],
        required_permission: Permission,
    ) -> bool:
        """Check if the given permissions include the required permission.

        Args:
            user_permissions: List or set of permissions to check
            required_permission: The permission to look for

        Returns:
            True if the required permission is in the user_permissions
        """
        return required_permission in user_permissions

    @classmethod
    def has_all_permissions(
        cls,
        user_permissions: List[Permission] | Set[Permission],
        required_permissions: List[Permission] | Set[Permission],
    ) -> bool:
        """Check if the given permissions include all the required permissions.

        Args:
            user_permissions: List or set of permissions to check
            required_permissions: List or set of permissions to look for

        Returns:
            True if all required permissions are in the user_permissions
        """
        if isinstance(required_permissions, list):
            required_permissions_set = set(required_permissions)
        else:
            required_permissions_set = required_permissions

        if isinstance(user_permissions, list):
            user_permissions_set = set(user_permissions)
        else:
            user_permissions_set = user_permissions

        return required_permissions_set.issubset(user_permissions_set)
