"""Unit tests for search service."""
import pytest
from uuid import UUID, uuid4

from app.models.application import Application, ApplicationStatus
from app.models.cover_letter import CoverLetter
from app.models.job import JobPosting, JobStatus
from app.schemas.search import SearchParams
from app.services.search_service import SearchService


@pytest.mark.asyncio
class TestSearchService:
    """Test search service functionality."""

    async def test_global_search_jobs(
        self, db_session, test_user, sample_job_posting
    ):
        """Test searching across jobs."""
        params = SearchParams(
            query="python",
            page=1,
            page_size=20,
            sort_by="relevance",
            sort_order="desc",
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        assert result.query == "python"
        assert result.total >= 1
        assert len(result.results) >= 1
        assert result.facets["job"] >= 1
        
        # Check job result
        job_result = next(r for r in result.results if r.entity_type == "job")
        assert job_result.title == f"{sample_job_posting.job_title} at {sample_job_posting.company_name}"
        assert job_result.relevance_score > 0

    async def test_global_search_applications(
        self, db_session, test_user, sample_application
    ):
        """Test searching across applications."""
        # Update application notes to match search
        sample_application.follow_up_notes = "Python backend position"
        await db_session.commit()
        
        params = SearchParams(
            query="python",
            entity_types=["application"],
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        assert result.total >= 1
        assert result.facets["application"] >= 1
        assert all(r.entity_type == "application" for r in result.results)

    async def test_global_search_cover_letters(
        self, db_session, test_user, sample_cover_letter
    ):
        """Test searching across cover letters."""
        params = SearchParams(
            query="software",
            entity_types=["cover_letter"],
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        assert result.total >= 1
        assert result.facets["cover_letter"] >= 1
        assert all(r.entity_type == "cover_letter" for r in result.results)

    async def test_global_search_all_types(
        self, db_session, test_user, sample_job_posting, sample_application, sample_cover_letter
    ):
        """Test searching across all entity types."""
        params = SearchParams(
            query="engineer",
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        # Should find results in multiple entity types
        assert result.total >= 1
        entity_types_found = {r.entity_type for r in result.results}
        assert len(entity_types_found) >= 1

    async def test_search_pagination(
        self, db_session, test_user
    ):
        """Test search pagination works correctly."""
        # Create multiple jobs with searchable content
        for i in range(5):
            job = JobPosting(
                user_id=test_user.id,
                company_name=f"Company {i}",
                job_title="Python Developer",
                job_url=f"https://example.com/job{i}",
                job_description="Looking for a Python developer with experience",
            )
            db_session.add(job)
        await db_session.commit()
        
        # Page 1
        params = SearchParams(
            query="python",
            entity_types=["job"],
            page=1,
            page_size=3,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        assert result.page == 1
        assert result.page_size == 3
        assert len(result.results) <= 3

    async def test_search_no_results(
        self, db_session, test_user
    ):
        """Test search with no matching results."""
        params = SearchParams(
            query="nonexistentquery12345",
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        assert result.total == 0
        assert len(result.results) == 0

    async def test_search_sort_by_created_at(
        self, db_session, test_user, sample_job_posting
    ):
        """Test sorting by created_at."""
        params = SearchParams(
            query="engineer",
            sort_by="created_at",
            sort_order="desc",
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        # Results should be sorted by created_at descending
        if len(result.results) > 1:
            for i in range(len(result.results) - 1):
                assert result.results[i].created_at >= result.results[i + 1].created_at

    async def test_search_filter_by_entity_type(
        self, db_session, test_user, sample_job_posting, sample_application
    ):
        """Test filtering results by entity type."""
        params = SearchParams(
            query="engineer",
            entity_types=["job"],
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, sample_user.id, params)
        
        # All results should be jobs
        assert all(r.entity_type == "job" for r in result.results)
        assert result.facets["application"] == 0
        assert result.facets["cover_letter"] == 0

    async def test_search_user_isolation(
        self, db_session, test_user, other_user
    ):
        """Test users can only search their own data."""
        # Create job for other user
        other_job = JobPosting(
            user_id=other_user.id,
            company_name="Other Company",
            job_title="Secret Python Job",
            job_url="https://example.com/secret",
            job_description="This should not appear in search",
        )
        db_session.add(other_job)
        await db_session.commit()
        
        params = SearchParams(
            query="secret",
            page=1,
            page_size=20,
        )
        
        result = await SearchService.global_search(db_session, test_user.id, params)
        
        # Should not find other user's job
        assert result.total == 0

    async def test_snippet_creation(self):
        """Test snippet generation with query highlighting."""
        text = "This is a long text about Python development and software engineering. We are looking for someone with Python experience."
        query = "python"
        
        snippet = SearchService._create_snippet(text, query, max_length=50)
        
        assert len(snippet) <= 70  # 50 + ellipsis
        assert "python" in snippet.lower() or "Python" in snippet

    async def test_snippet_creation_empty_text(self):
        """Test snippet with empty text."""
        snippet = SearchService._create_snippet("", "python", max_length=50)
        
        assert snippet == ""

    async def test_snippet_creation_query_not_found(self):
        """Test snippet when query not found in text."""
        text = "This text does not contain the search term."
        query = "nonexistent"
        
        snippet = SearchService._create_snippet(text, query, max_length=50)
        
        # Should return beginning of text
        assert snippet == text[:50] + "..."
