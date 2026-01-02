"""Search schemas for global search functionality."""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema


class SearchParams(BaseSchema):
    """Parameters for global search."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    entity_types: Optional[list[Literal["job", "application", "cover_letter"]]] = Field(
        None, description="Filter by entity types"
    )
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Results per page")
    sort_by: Literal["relevance", "created_at", "updated_at"] = Field(
        "relevance", description="Sort field"
    )
    sort_order: Literal["asc", "desc"] = Field("desc", description="Sort order")

    @field_validator("entity_types")
    @classmethod
    def validate_entity_types(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Ensure entity types are unique if provided."""
        if v is not None and len(v) != len(set(v)):
            raise ValueError("entity_types must contain unique values")
        return v


class SearchResultItem(BaseSchema):
    """Individual search result."""

    id: UUID
    entity_type: Literal["job", "application", "cover_letter"]
    title: str = Field(..., description="Result title")
    snippet: str = Field(..., description="Text snippet with search term highlighted")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    created_at: datetime
    updated_at: datetime
    
    # Entity-specific metadata
    metadata: dict = Field(default_factory=dict, description="Entity-specific data")


class SearchResponse(BaseSchema):
    """Search results response."""

    query: str
    total: int
    page: int
    page_size: int
    results: list[SearchResultItem]
    facets: dict = Field(
        default_factory=dict,
        description="Result counts by entity type"
    )
