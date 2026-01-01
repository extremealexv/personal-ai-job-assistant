"""Unit tests for rate limiting service."""
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.core.ai_exceptions import RateLimitError
from app.services.rate_limit_service import RateLimitService


@pytest.fixture
def rate_limiter():
    """Create a fresh rate limiter for each test."""
    return RateLimitService()


class TestRateLimitBasics:
    """Test basic rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, rate_limiter):
        """Test that first request is always allowed."""
        user_id = uuid4()

        # Should not raise
        await rate_limiter.check_rate_limit(user_id)
        await rate_limiter.record_request(user_id)

    @pytest.mark.asyncio
    async def test_anonymous_user_allowed(self, rate_limiter):
        """Test that anonymous users can make requests."""
        # Should not raise
        await rate_limiter.check_rate_limit(None)
        await rate_limiter.record_request(None)

    @pytest.mark.asyncio
    async def test_under_limit_allowed(self, rate_limiter):
        """Test requests under limit are allowed."""
        user_id = uuid4()

        # Make 5 requests (under default limit of 10)
        for _ in range(5):
            await rate_limiter.check_rate_limit(user_id)
            await rate_limiter.record_request(user_id)


class TestPerMinuteRateLimit:
    """Test per-minute rate limiting."""

    @pytest.mark.asyncio
    async def test_per_minute_limit_enforced(self, rate_limiter):
        """Test that per-minute limit is enforced."""
        user_id = uuid4()
        limit = rate_limiter.requests_per_minute

        # Fill up to the limit
        for _ in range(limit):
            await rate_limiter.check_rate_limit(user_id)
            await rate_limiter.record_request(user_id)

        # Next request should fail
        with pytest.raises(RateLimitError) as exc_info:
            await rate_limiter.check_rate_limit(user_id)

        assert "per minute" in str(exc_info.value).lower()
        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_different_users_independent_limits(self, rate_limiter):
        """Test that different users have independent limits."""
        user1 = uuid4()
        user2 = uuid4()
        limit = rate_limiter.requests_per_minute

        # User 1 hits limit
        for _ in range(limit):
            await rate_limiter.check_rate_limit(user1)
            await rate_limiter.record_request(user1)

        # User 1 should be blocked
        with pytest.raises(RateLimitError):
            await rate_limiter.check_rate_limit(user1)

        # User 2 should still be allowed
        await rate_limiter.check_rate_limit(user2)
        await rate_limiter.record_request(user2)


class TestDailyRateLimit:
    """Test daily rate limiting."""

    @pytest.mark.asyncio
    async def test_daily_limit_enforced(self, rate_limiter):
        """Test that daily limit is enforced."""
        user_id = uuid4()

        # Override with smaller limit for testing
        rate_limiter.requests_per_day = 5

        # Fill up to the limit
        for _ in range(5):
            await rate_limiter.check_rate_limit(user_id)
            await rate_limiter.record_request(user_id)

        # Next request should fail
        with pytest.raises(RateLimitError) as exc_info:
            await rate_limiter.check_rate_limit(user_id)

        assert "daily" in str(exc_info.value).lower()
        assert exc_info.value.retry_after > 0  # Should be seconds until midnight

    @pytest.mark.asyncio
    async def test_daily_counter_resets_on_new_day(self, rate_limiter):
        """Test that daily counter resets on new day."""
        user_id = uuid4()
        user_key = str(user_id)

        # Make a request
        await rate_limiter.check_rate_limit(user_id)
        await rate_limiter.record_request(user_id)

        # Simulate yesterday's date
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
        rate_limiter._rate_limits[user_key]["day"] = yesterday
        rate_limiter._rate_limits[user_key]["daily_requests"] = 100  # Set to high number

        # Check limit (should reset)
        await rate_limiter.check_rate_limit(user_id)

        # Verify reset
        assert rate_limiter._rate_limits[user_key]["daily_requests"] == 100  # Not reset until record_request


class TestOldRequestCleanup:
    """Test cleanup of old requests."""

    @pytest.mark.asyncio
    async def test_old_requests_cleaned_up(self, rate_limiter):
        """Test that requests older than 1 minute are cleaned up."""
        user_id = uuid4()
        user_key = str(user_id)

        # Make a request
        await rate_limiter.check_rate_limit(user_id)
        await rate_limiter.record_request(user_id)

        # Manually set timestamp to 2 minutes ago
        two_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=2)
        rate_limiter._rate_limits[user_key]["requests"] = [two_minutes_ago]

        # Check remaining (should trigger cleanup)
        remaining = await rate_limiter.get_remaining_requests(user_id)

        # Old request should be cleaned up
        assert remaining["remaining_minute"] == rate_limiter.requests_per_minute


class TestRemainingRequests:
    """Test get_remaining_requests functionality."""

    @pytest.mark.asyncio
    async def test_remaining_requests_initial(self, rate_limiter):
        """Test remaining requests for new user."""
        user_id = uuid4()

        remaining = await rate_limiter.get_remaining_requests(user_id)

        assert remaining["remaining_minute"] == rate_limiter.requests_per_minute
        assert remaining["remaining_day"] == rate_limiter.requests_per_day

    @pytest.mark.asyncio
    async def test_remaining_requests_after_use(self, rate_limiter):
        """Test remaining requests decreases after use."""
        user_id = uuid4()

        # Make 3 requests
        for _ in range(3):
            await rate_limiter.check_rate_limit(user_id)
            await rate_limiter.record_request(user_id)

        remaining = await rate_limiter.get_remaining_requests(user_id)

        assert remaining["remaining_minute"] == rate_limiter.requests_per_minute - 3
        assert remaining["remaining_day"] == rate_limiter.requests_per_day - 3


class TestResetUserLimits:
    """Test resetting user limits."""

    @pytest.mark.asyncio
    async def test_reset_user_limits(self, rate_limiter):
        """Test resetting limits for a user."""
        user_id = uuid4()
        limit = rate_limiter.requests_per_minute

        # Fill up to limit
        for _ in range(limit):
            await rate_limiter.check_rate_limit(user_id)
            await rate_limiter.record_request(user_id)

        # Should be blocked
        with pytest.raises(RateLimitError):
            await rate_limiter.check_rate_limit(user_id)

        # Reset
        await rate_limiter.reset_user_limits(user_id)

        # Should be allowed now
        await rate_limiter.check_rate_limit(user_id)
        await rate_limiter.record_request(user_id)

    @pytest.mark.asyncio
    async def test_reset_nonexistent_user(self, rate_limiter):
        """Test resetting limits for user with no data."""
        user_id = uuid4()

        # Should not raise
        await rate_limiter.reset_user_limits(user_id)
