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

    READ_MEMBER = "member:read"
    LIST_MEMBERS = "member:list"
    INVITE_MEMBER = "member:invite"
    CANCEL_INVITE = "member:cancel_invite"
    UPDATE_MEMBER_ROLE = "member:update_role"
    REMOVE_MEMBER = "member:remove"

    CREATE_AGENT = "agent:create"
    READ_AGENT = "agent:read"
    LIST_AGENTS = "agent:list"
    UPDATE_AGENT = "agent:update"
    DELETE_AGENT = "agent:delete"

    CREATE_CREDENTIAL = "credential:create"
    READ_CREDENTIAL = "credential:read"
    LIST_CREDENTIALS = "credential:list"
    UPDATE_CREDENTIAL = "credential:update"
    DELETE_CREDENTIAL = "credential:delete"

    UPLOAD_FILE = "file:upload"
    READ_FILE = "file:read"
    LIST_FILES = "file:list"
    UPDATE_FILE = "file:update"
    DELETE_FILE = "file:delete"

    CREATE_VECTOR_STORE = "vector_store:create"
    READ_VECTOR_STORE = "vector_store:read"
    LIST_VECTOR_STORES = "vector_store:list"
    UPDATE_VECTOR_STORE = "vector_store:update"
    DELETE_VECTOR_STORE = "vector_store:delete"

    CREATE_CHANNEL = "channel:create"
    READ_CHANNEL = "channel:read"
    LIST_CHANNELS = "channel:list"
    UPDATE_CHANNEL = "channel:update"
    DELETE_CHANNEL = "channel:delete"

    CREATE_CONTACT = "contact:create"
    READ_CONTACT = "contact:read"
    LIST_CONTACTS = "contact:list"
    UPDATE_CONTACT = "contact:update"
    DELETE_CONTACT = "contact:delete"

    READ_MESSAGES = "messages:read"
    SEND_MESSAGES = "messages:send"
    DELETE_MESSAGES = "messages:delete"

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


@unique
class PlatformPermission(StrEnum):
    """Standard permission strings for Spryx platform.

    Permissions follow the format `resource:action` where:
    - resource: The entity being accessed (organization, application, etc.)
    - action: The operation being performed (read, write, etc.)
    """

    ADMIN_ORGANIZATIONS = "organizations:admin"

    CREATE_ORGANIZATION = "organization:create"

    UPDATE_USER_PLATFORM_ROLE = "user:update_platform_role"

    # Application permissions
    CREATE_APPLICATION = "application:create"
    READ_APPLICATION = "application:read"
    LIST_APPLICATIONS = "application:list"
    UPDATE_APPLICATION = "application:update"
    DELETE_APPLICATION = "application:delete"

    # Plan permissions
    CREATE_PLAN = "plan:create"
    READ_PLAN = "plan:read"
    LIST_PLANS = "plan:list"
    UPDATE_PLAN = "plan:update"
    DELETE_PLAN = "plan:delete"

    # User permissions
    CREATE_USER = "user:create"
    READ_USER = "user:read"
    LIST_USERS = "user:list"
    UPDATE_USER = "user:update"
    DELETE_USER = "user:delete"

    # Add more permissions as needed
