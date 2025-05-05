from pydantic import BaseModel, Field

from spryx_core.id import EntityId
from spryx_core.security.permissions import Permission


class OrganizationRole(BaseModel):
    """Role of a user in an organization."""

    id: EntityId = Field(..., description="ID of the role")
    name: str = Field(..., description="Name of the role")
    permissions: set[Permission] = Field(..., description="Permissions of the role")


class CurrentOrganization(BaseModel):
    """Current organization of a user."""

    id: EntityId = Field(..., description="ID of the organization")
    name: str = Field(..., description="Name of the organization")
    role: OrganizationRole = Field(
        ..., description="Role of the user in the organization"
    )
