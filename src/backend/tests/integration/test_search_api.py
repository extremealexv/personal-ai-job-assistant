"""Integration tests for search API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSearchAPI:
    """Test search API endpoints."""

    async def test_search_endpoint_success(
        self, client: AsyncClient, auth_headers, sample_job_posting
    ):
        """Test successful search."""
        response = await client.get(
            "/api/v1/search",
            params={"query": "engineer"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "total" in data
        assert "results" in data
        assert "facets" in data

    async def test_search_without_auth(self, client: AsyncClient):
        """Test search without authentication returns 403."""
        response = await client.get(
            "/api/v1/search",
            params={"query": "test"},
        )
        
        assert response.status_code == 403

    async def test_search_finds_jobs(
        self, client: AsyncClient, auth_headers, sample_job_posting
    ):
        """Test search finds job postings."""
        response = await client.get(
            "/api/v1/search",
            params={
                "query": sample_job_posting.job_title,
                "entity_types": ["job"],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["results"]) >= 1
        assert data["results"][0]["entity_type"] == "job"

    async def test_search_with_pagination(
        self, client: AsyncClient, auth_headers, sample_job_posting
    ):
        """Test search pagination."""
        response = await client.get(
            "/api/v1/search",
            params={
                "query": "engineer",
                "page": 1,
                "page_size": 5,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["results"]) <= 5

    async def test_search_filter_by_entity_type(
        self, client: AsyncClient, auth_headers, sample_job_posting, sample_application
    ):
        """Test filtering search by entity type."""
        response = await client.get(
            "/api/v1/search",
            params={
                "query": "engineer",
                "entity_types": ["job"],
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All results should be jobs
        for result in data["results"]:
            assert result["entity_type"] == "job"

    async def test_search_sort_by_relevance(
        self, client: AsyncClient, auth_headers, sample_job_posting
    ):
        """Test sorting search results by relevance."""
        response = await client.get(
            "/api/v1/search",
            params={
                "query": "engineer",
                "sort_by": "relevance",
                "sort_order": "desc",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Results should be sorted by relevance (highest first)
        if len(data["results"]) > 1:
            for i in range(len(data["results"]) - 1):
                assert data["results"][i]["relevance_score"] >= data["results"][i + 1]["relevance_score"]

    async def test_search_no_results(
        self, client: AsyncClient, auth_headers
    ):
        """Test search with no matching results."""
        response = await client.get(
            "/api/v1/search",
            params={"query": "xyznonexistentquery123"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    async def test_search_user_isolation(
        self, client: AsyncClient, auth_headers, other_user_job
    ):
        """Test search only returns current user's data."""
        response = await client.get(
            "/api/v1/search",
            params={"query": other_user_job.job_title},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not find other user's job
        for result in data["results"]:
            assert result["entity_type"] != "job" or result["title"] != other_user_job.job_title

    async def test_search_invalid_sort_by(
        self, client: AsyncClient, auth_headers
    ):
        """Test search with invalid sort_by parameter."""
        response = await client.get(
            "/api/v1/search",
            params={
                "query": "engineer",
                "sort_by": "invalid_field",
            },
            headers=auth_headers,
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422

    async def test_search_facets(
        self, client: AsyncClient, auth_headers, sample_job_posting, sample_application
    ):
        """Test search returns facets with entity type counts."""
        response = await client.get(
            "/api/v1/search",
            params={"query": "engineer"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "facets" in data
        assert isinstance(data["facets"], dict)
        # Should have counts for entity types that matched
        if data["total"] > 0:
            assert any(count > 0 for count in data["facets"].values())
