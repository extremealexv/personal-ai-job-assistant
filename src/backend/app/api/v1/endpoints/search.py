"""Search API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.search import SearchParams, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def global_search(
    query: str = Query(..., min_length=1, max_length=500, description="Search query"),
    entity_types: list[str] | None = Query(None, description="Filter by entity types"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("relevance", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    """
    Global search across jobs, applications, and cover letters.
    
    - **query**: Search term (required)
    - **entity_types**: Filter results by type (optional): job, application, cover_letter
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    - **sort_by**: Sort field - relevance, created_at, updated_at (default: relevance)
    - **sort_order**: Sort order - asc, desc (default: desc)
    
    Returns search results with relevance scoring and snippets.
    """
    params = SearchParams(
        query=query,
        entity_types=entity_types,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    return await SearchService.global_search(db, current_user.id, params)
