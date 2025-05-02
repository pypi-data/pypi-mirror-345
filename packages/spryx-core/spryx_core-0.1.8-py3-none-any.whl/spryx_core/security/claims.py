"""
JWT claims validation models for Spryx authentication.

This module provides Pydantic models for validating and working with JWT claims
used in Spryx authentication system. It includes models for different token types
(user and application tokens) with automatic discrimination between them.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Literal, Optional, Union, get_args

from pydantic import BaseModel, Field, model_validator

from spryx_core.id import EntityId
from spryx_core.security.value_objects import CurrentOrganization

from .permissions import PlatformPermission


class _CoreModel(BaseModel):
    """Shared Pydantic config for core models."""

    model_config = {
        "extra": "forbid",
        "frozen": True,  # immutable instances
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class BaseClaims(_CoreModel):
    """Fields common to every access token issued by Spryx Auth."""

    iss: str = Field(..., description="Issuer of the token")
    sub: str = Field(..., description="Subject of the token (user or app ID)")
    aud: str = Field(..., description="Audience for the token (client ID)")
    iat: datetime = Field(..., description="Issued at timestamp")
    jti: str = Field(..., description="JWT ID")
    exp: datetime = Field(..., description="Expiration timestamp")
    token_type: str = Field(..., frozen=True, description="Type of token (user or app)")

    @model_validator(mode="after")
    def _check_exp(self):
        """Validate that the token hasn't expired."""
        if self.exp < datetime.now(UTC):
            raise ValueError("token already expired")
        return self


class UserClaims(BaseClaims):
    """Token issued to a *human* user belonging to an organization."""

    token_type: Literal["user"] = Field(
        ..., description="Must be 'user' for user tokens"
    )
    name: str = Field(..., description="Name of the user")
    email: str = Field(..., description="Email of the user")
    image: Optional[str] = Field(None, description="Image of the user")
    current_organization: Optional[CurrentOrganization] = Field(
        None, description="Current organization of the user"
    )
    allowed_org_ids: list[EntityId] = Field(
        default_factory=list, description="IDs of organizations the user has access to"
    )
    platform_role: str = Field(..., description="Role of the user")
    platform_permissions: list[PlatformPermission] = Field(
        default_factory=list, description="Permissions of the user"
    )


class AppClaims(BaseClaims):
    """Token issued to a *machine* / application integrating with Spryx."""

    token_type: Literal["app"] = Field(
        ..., description="Must be 'app' for application tokens"
    )


# Discriminated union → automatic down-casting after validation
TokenClaims = Annotated[
    Union[UserClaims, AppClaims],
    Field(discriminator="token_type"),
]
TOKEN_CLAIMS_TYPES = get_args(TokenClaims)
