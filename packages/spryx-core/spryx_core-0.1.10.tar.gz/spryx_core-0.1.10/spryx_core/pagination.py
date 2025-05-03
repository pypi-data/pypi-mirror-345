"""
Pagination models and utilities.

This module provides standardized models for implementing and handling paginated
results in APIs and data retrieval operations.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Generic, List, Optional, TypeVar, Literal, TypeAlias

T = TypeVar("T")
SortOrder: TypeAlias = Literal["asc", "desc"]

class Page(BaseModel, Generic[T]):
    """
    Generic pagination model that can be used for any type of paginated data.

    This model represents a paginated response with metadata about the pagination
    state and the actual items for the current page.
    """

    items: List[T] = Field(..., description="The items in the current page of results")
    page: int = Field(..., description="Current page number (1-based)", ge=1)
    page_size: int = Field(..., description="Number of items per page", gt=0)
    total: int = Field(..., description="Total number of items across all pages", ge=0)

    @computed_field
    def total_pages(self) -> int:
        """Calculate the total number of pages."""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @computed_field
    def has_previous(self) -> bool:
        """Check if there is a previous page available."""
        return self.page > 1

    @computed_field
    def has_next(self) -> bool:
        """Check if there is a next page available."""
        return self.page < self.total_pages

    @computed_field
    def next_page(self) -> Optional[int]:
        """Get the next page number, if available."""
        return self.page + 1 if self.has_next else None

    @computed_field
    def previous_page(self) -> Optional[int]:
        """Get the previous page number, if available."""
        return self.page - 1 if self.has_previous else None

class PageFilter(BaseModel):
    page: int = Field(default=1, gt=0)
    limit: int = Field(default=10, gt=0, le=100)
    order: SortOrder = Field(default="asc")