"""Unit tests for cost tracking service."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.core.ai_exceptions import AIProviderError
from app.services.cost_tracking_service import CostTrackingService


@pytest.fixture
def cost_tracker():
    """Create a fresh cost tracker for each test."""
    tracker = CostTrackingService()
    # Use smaller budget for testing
    tracker.monthly_budget = 10.0
    return tracker


class TestCostTrackingBasics:
    """Test basic cost tracking functionality."""

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, cost_tracker):
        """Test that first request is allowed."""
        user_id = uuid4()

        # Should not raise
        await cost_tracker.check_budget_limit(user_id, estimated_cost=0.5)

    @pytest.mark.asyncio
    async def test_record_cost(self, cost_tracker):
        """Test recording cost."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=1.5)

        usage = await cost_tracker.get_monthly_usage(user_id)
        assert usage["total_cost"] == 1.5

    @pytest.mark.asyncio
    async def test_multiple_costs_accumulate(self, cost_tracker):
        """Test that multiple costs accumulate."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=1.0)
        await cost_tracker.record_cost(user_id, cost=2.5)
        await cost_tracker.record_cost(user_id, cost=0.5)

        usage = await cost_tracker.get_monthly_usage(user_id)
        assert usage["total_cost"] == 4.0


class TestBudgetLimits:
    """Test budget limit enforcement."""

    @pytest.mark.asyncio
    async def test_budget_limit_enforced(self, cost_tracker):
        """Test that budget limit is enforced."""
        user_id = uuid4()

        # Record costs up to limit
        await cost_tracker.record_cost(user_id, cost=9.0)

        # This should exceed the $10 limit
        with pytest.raises(AIProviderError) as exc_info:
            await cost_tracker.check_budget_limit(user_id, estimated_cost=2.0)

        assert "budget limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_budget_allows_exact_limit(self, cost_tracker):
        """Test that exactly hitting budget is allowed."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=9.0)

        # Should allow exactly hitting the limit
        await cost_tracker.check_budget_limit(user_id, estimated_cost=1.0)

    @pytest.mark.asyncio
    async def test_different_users_independent_budgets(self, cost_tracker):
        """Test that different users have independent budgets."""
        user1 = uuid4()
        user2 = uuid4()

        # User 1 uses full budget
        await cost_tracker.record_cost(user1, cost=10.0)

        # User 1 should be blocked
        with pytest.raises(AIProviderError):
            await cost_tracker.check_budget_limit(user1, estimated_cost=0.1)

        # User 2 should still be allowed
        await cost_tracker.check_budget_limit(user2, estimated_cost=5.0)


class TestMonthlyUsage:
    """Test monthly usage reporting."""

    @pytest.mark.asyncio
    async def test_monthly_usage_initial(self, cost_tracker):
        """Test monthly usage for new user."""
        user_id = uuid4()

        usage = await cost_tracker.get_monthly_usage(user_id)

        assert usage["total_cost"] == 0.0
        assert usage["budget_limit"] == 10.0
        assert usage["remaining_budget"] == 10.0
        assert usage["percentage_used"] == 0.0

    @pytest.mark.asyncio
    async def test_monthly_usage_after_use(self, cost_tracker):
        """Test monthly usage after some use."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=3.0)

        usage = await cost_tracker.get_monthly_usage(user_id)

        assert usage["total_cost"] == 3.0
        assert usage["remaining_budget"] == 7.0
        assert usage["percentage_used"] == 30.0

    @pytest.mark.asyncio
    async def test_monthly_usage_over_budget(self, cost_tracker):
        """Test usage when over budget."""
        user_id = uuid4()

        # Somehow record more than budget (shouldn't happen in practice)
        await cost_tracker.record_cost(user_id, cost=12.0)

        usage = await cost_tracker.get_monthly_usage(user_id)

        assert usage["total_cost"] == 12.0
        assert usage["remaining_budget"] == 0.0  # Can't be negative
        assert usage["percentage_used"] == 120.0


class TestMonthlyReset:
    """Test monthly cost reset."""

    @pytest.mark.asyncio
    async def test_monthly_reset_on_new_month(self, cost_tracker):
        """Test that costs reset on new month."""
        user_id = uuid4()
        user_key = str(user_id)

        # Record cost
        await cost_tracker.record_cost(user_id, cost=5.0)

        # Simulate last month
        last_month_year = 2025
        last_month_month = 11
        cost_tracker._cost_cache[user_key]["month"] = (last_month_year, last_month_month)

        # Check usage (should trigger reset)
        usage = await cost_tracker.get_monthly_usage(user_id)

        # Cost should be reset
        assert usage["total_cost"] == 0.0


class TestCostWarnings:
    """Test cost warning thresholds."""

    @pytest.mark.asyncio
    async def test_no_warning_under_80_percent(self, cost_tracker):
        """Test no warning when under 80% of budget."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=7.0)  # 70%

        warning = await cost_tracker.get_cost_warning_threshold(user_id)
        assert warning is None

    @pytest.mark.asyncio
    async def test_warning_at_80_percent(self, cost_tracker):
        """Test warning at 80% of budget."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=8.0)  # 80%

        warning = await cost_tracker.get_cost_warning_threshold(user_id)
        assert warning is not None
        assert "80.0%" in warning
        assert "WARNING" in warning

    @pytest.mark.asyncio
    async def test_critical_at_90_percent(self, cost_tracker):
        """Test critical warning at 90% of budget."""
        user_id = uuid4()

        await cost_tracker.record_cost(user_id, cost=9.0)  # 90%

        warning = await cost_tracker.get_cost_warning_threshold(user_id)
        assert warning is not None
        assert "90.0%" in warning
        assert "CRITICAL" in warning


class TestResetUserCosts:
    """Test resetting user costs."""

    @pytest.mark.asyncio
    async def test_reset_user_costs(self, cost_tracker):
        """Test resetting costs for a user."""
        user_id = uuid4()

        # Record costs
        await cost_tracker.record_cost(user_id, cost=10.0)

        # Should be over budget
        with pytest.raises(AIProviderError):
            await cost_tracker.check_budget_limit(user_id, estimated_cost=0.1)

        # Reset
        await cost_tracker.reset_user_costs(user_id)

        # Should be allowed now
        await cost_tracker.check_budget_limit(user_id, estimated_cost=5.0)

    @pytest.mark.asyncio
    async def test_reset_nonexistent_user(self, cost_tracker):
        """Test resetting costs for user with no data."""
        user_id = uuid4()

        # Should not raise
        await cost_tracker.reset_user_costs(user_id)


class TestAnonymousUser:
    """Test anonymous user cost tracking."""

    @pytest.mark.asyncio
    async def test_anonymous_user_tracking(self, cost_tracker):
        """Test that anonymous users are tracked."""
        await cost_tracker.record_cost(None, cost=3.0)

        usage = await cost_tracker.get_monthly_usage(None)
        assert usage["total_cost"] == 3.0

    @pytest.mark.asyncio
    async def test_anonymous_user_budget_limit(self, cost_tracker):
        """Test that anonymous users have budget limits."""
        await cost_tracker.record_cost(None, cost=10.0)

        with pytest.raises(AIProviderError):
            await cost_tracker.check_budget_limit(None, estimated_cost=0.5)
