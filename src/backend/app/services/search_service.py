"""Search service for global search across entities."""
from typing import Optional
from uuid import UUID

from sqlalchemy import Float, and_, case, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.cover_letter import CoverLetter
from app.models.job import JobPosting
from app.schemas.search import SearchParams, SearchResponse, SearchResultItem


class SearchService:
    """Service for global search functionality."""

    @staticmethod
    async def global_search(
        db: AsyncSession,
        user_id: UUID,
        params: SearchParams,
    ) -> SearchResponse:
        """
        Perform global search across jobs, applications, and cover letters.
        
        Args:
            db: Database session
            user_id: User ID for authorization
            params: Search parameters
            
        Returns:
            SearchResponse with results and facets
        """
        results = []
        facets = {"job": 0, "application": 0, "cover_letter": 0}
        
        # Determine which entities to search
        entity_types = params.entity_types or ["job", "application", "cover_letter"]
        
        # Search jobs
        if "job" in entity_types:
            job_results = await SearchService._search_jobs(db, user_id, params)
            results.extend(job_results)
            facets["job"] = len(job_results)
        
        # Search applications
        if "application" in entity_types:
            app_results = await SearchService._search_applications(db, user_id, params)
            results.extend(app_results)
            facets["application"] = len(app_results)
        
        # Search cover letters
        if "cover_letter" in entity_types:
            cl_results = await SearchService._search_cover_letters(db, user_id, params)
            results.extend(cl_results)
            facets["cover_letter"] = len(cl_results)
        
        # Sort results
        if params.sort_by == "relevance":
            results.sort(key=lambda x: x.relevance_score, reverse=(params.sort_order == "desc"))
        elif params.sort_by == "created_at":
            results.sort(key=lambda x: x.created_at, reverse=(params.sort_order == "desc"))
        elif params.sort_by == "updated_at":
            results.sort(key=lambda x: x.updated_at, reverse=(params.sort_order == "desc"))
        
        # Paginate
        total = len(results)
        start = (params.page - 1) * params.page_size
        end = start + params.page_size
        page_results = results[start:end]
        
        return SearchResponse(
            query=params.query,
            total=total,
            page=params.page,
            page_size=params.page_size,
            results=page_results,
            facets=facets,
        )

    @staticmethod
    async def _search_jobs(
        db: AsyncSession, 
        user_id: UUID, 
        params: SearchParams
    ) -> list[SearchResultItem]:
        """Search job postings."""
        query_lower = params.query.lower()
        
        # Build query with relevance scoring
        stmt = select(
            JobPosting,
            # Calculate relevance score
            case(
                (func.lower(JobPosting.job_title).contains(query_lower), 1.0),
                (func.lower(JobPosting.company_name).contains(query_lower), 0.9),
                (func.lower(JobPosting.job_description).contains(query_lower), 0.7),
                else_=0.5
            ).label("relevance")
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
                or_(
                    func.lower(JobPosting.job_title).contains(query_lower),
                    func.lower(JobPosting.company_name).contains(query_lower),
                    func.lower(JobPosting.job_description).contains(query_lower),
                    func.lower(JobPosting.location).contains(query_lower),
                )
            )
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        search_results = []
        for job, relevance in rows:
            # Create snippet
            snippet = SearchService._create_snippet(
                job.job_description or "",
                query_lower,
                max_length=200
            )
            
            search_results.append(
                SearchResultItem(
                    id=job.id,
                    entity_type="job",
                    title=f"{job.job_title} at {job.company_name}",
                    snippet=snippet,
                    relevance_score=float(relevance),
                    created_at=job.created_at,
                    updated_at=job.updated_at,
                    metadata={
                        "company_name": job.company_name,
                        "job_title": job.job_title,
                        "status": job.status,
                        "interest_level": job.interest_level,
                        "location": job.location,
                    }
                )
            )
        
        return search_results

    @staticmethod
    async def _search_applications(
        db: AsyncSession,
        user_id: UUID,
        params: SearchParams
    ) -> list[SearchResultItem]:
        """Search applications."""
        query_lower = params.query.lower()
        
        # Join with job posting for search
        stmt = select(
            Application,
            JobPosting,
            case(
                (func.lower(JobPosting.job_title).contains(query_lower), 1.0),
                (func.lower(JobPosting.company_name).contains(query_lower), 0.9),
                (func.lower(Application.follow_up_notes).contains(query_lower), 0.8),
                else_=0.5
            ).label("relevance")
        ).join(
            JobPosting, Application.job_posting_id == JobPosting.id
        ).where(
            and_(
                Application.user_id == user_id,
                or_(
                    func.lower(JobPosting.job_title).contains(query_lower),
                    func.lower(JobPosting.company_name).contains(query_lower),
                    func.lower(Application.follow_up_notes).contains(query_lower),
                )
            )
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        search_results = []
        for app, job, relevance in rows:
            snippet = SearchService._create_snippet(
                app.follow_up_notes or f"Application to {job.company_name}",
                query_lower,
                max_length=200
            )
            
            search_results.append(
                SearchResultItem(
                    id=app.id,
                    entity_type="application",
                    title=f"Application: {job.job_title} at {job.company_name}",
                    snippet=snippet,
                    relevance_score=float(relevance),
                    created_at=app.created_at,
                    updated_at=app.updated_at,
                    metadata={
                        "status": app.status,
                        "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
                        "job_title": job.job_title,
                        "company_name": job.company_name,
                    }
                )
            )
        
        return search_results

    @staticmethod
    async def _search_cover_letters(
        db: AsyncSession,
        user_id: UUID,
        params: SearchParams
    ) -> list[SearchResultItem]:
        """Search cover letters."""
        query_lower = params.query.lower()
        
        # Join with application and job for context
        stmt = select(
            CoverLetter,
            Application,
            JobPosting,
            case(
                (func.lower(CoverLetter.content).contains(query_lower), 1.0),
                else_=0.5
            ).label("relevance")
        ).join(
            Application, CoverLetter.application_id == Application.id
        ).join(
            JobPosting, Application.job_posting_id == JobPosting.id
        ).where(
            and_(
                Application.user_id == user_id,
                func.lower(CoverLetter.content).contains(query_lower),
            )
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        search_results = []
        for cl, app, job, relevance in rows:
            snippet = SearchService._create_snippet(
                cl.content,
                query_lower,
                max_length=200
            )
            
            search_results.append(
                SearchResultItem(
                    id=cl.id,
                    entity_type="cover_letter",
                    title=f"Cover Letter v{cl.version_number}: {job.job_title} at {job.company_name}",
                    snippet=snippet,
                    relevance_score=float(relevance),
                    created_at=cl.created_at,
                    updated_at=cl.updated_at,
                    metadata={
                        "version_number": cl.version_number,
                        "is_active": cl.is_active,
                        "tone": cl.tone,
                        "job_title": job.job_title,
                        "company_name": job.company_name,
                    }
                )
            )
        
        return search_results

    @staticmethod
    def _create_snippet(text: str, query: str, max_length: int = 200) -> str:
        """
        Create a text snippet highlighting the search term.
        
        Args:
            text: Full text to extract snippet from
            query: Search query
            max_length: Maximum snippet length
            
        Returns:
            Text snippet with query highlighted
        """
        if not text:
            return ""
        
        text_lower = text.lower()
        query_pos = text_lower.find(query)
        
        if query_pos == -1:
            # Query not found, return beginning of text
            return text[:max_length] + ("..." if len(text) > max_length else "")
        
        # Calculate snippet boundaries
        snippet_start = max(0, query_pos - max_length // 2)
        snippet_end = min(len(text), query_pos + len(query) + max_length // 2)
        
        snippet = text[snippet_start:snippet_end]
        
        # Add ellipsis if needed
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(text):
            snippet = snippet + "..."
        
        # Highlight the query term (simple version - could be improved with HTML)
        # For now, just uppercase the matching term
        return snippet
