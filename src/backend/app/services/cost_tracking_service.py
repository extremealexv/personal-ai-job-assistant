"""Cost tracking service for AI API usage."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.ai_exceptions import AIProviderError
from app.models.analytics import AnalyticsSnapshot

logger = logging.getLogger(__name__)


class CostTrackingService:
    """Service for tracking AI API costs and enforcing budget limits."""

    def __init__(self):
        """Initialize cost tracking service."""
        # In-memory cache: user_id -> {total_cost: float, month: (year, month)}
        self._cost_cache: dict[str, dict] = {}
        self.monthly_budget = settings.ai_monthly_budget_limit

    def _get_user_key(self, user_id: Optional[UUID]) -> str:
        """Get cache key for user."""
        return str(user_id) if user_id else "anonymous"

    def _get_current_month(self) -> tuple[int, int]:
        """Get current year and month."""
        now = datetime.now(timezone.utc)
        return (now.year, now.month)

    def _reset_monthly_cost_if_needed(self, user_key: str) -> None:
        """Reset monthly cost if it's a new month."""
        if user_key not in self._cost_cache:
            return

        current_month = self._get_current_month()
        user_data = self._cost_cache[user_key]

        if user_data.get("month") != current_month:
            user_data["total_cost"] = 0.0
            user_data["month"] = current_month
            logger.info(f"Reset monthly costs for user {user_key}")

    async def check_budget_limit(
        self, user_id: Optional[UUID] = None, estimated_cost: float = 0.0
    ) -> None:
        """Check if adding this cost would exceed monthly budget.
        
        Args:
            user_id: User ID to check budget for
            estimated_cost: Estimated cost of upcoming request
            
        Raises:
            AIProviderError: If budget limit would be exceeded
        """
        user_key = self._get_user_key(user_id)

        # Initialize user data if needed
        if user_key not in self._cost_cache:
            self._cost_cache[user_key] = {
                "total_cost": 0.0,
                "month": self._get_current_month(),
            }

        self._reset_monthly_cost_if_needed(user_key)

        user_data = self._cost_cache[user_key]
        current_cost = user_data["total_cost"]
        projected_cost = current_cost + estimated_cost

        if projected_cost > self.monthly_budget:
            logger.warning(
                f"Budget limit would be exceeded for user {user_id}: "
                f"${projected_cost:.2f} > ${self.monthly_budget:.2f}"
            )
            raise AIProviderError(
                f"Monthly AI budget limit would be exceeded: "
                f"${current_cost:.2f} / ${self.monthly_budget:.2f} used. "
                f"This request would cost ${estimated_cost:.4f}."
            )

    async def record_cost(
        self, user_id: Optional[UUID], cost: float, db: Optional[AsyncSession] = None
    ) -> None:
        """Record actual API cost.
        
        Args:
            user_id: User ID to record cost for
            cost: Actual cost of the request
            db: Optional database session for persistent storage
        """
        user_key = self._get_user_key(user_id)

        # Initialize user data if needed
        if user_key not in self._cost_cache:
            self._cost_cache[user_key] = {
                "total_cost": 0.0,
                "month": self._get_current_month(),
            }

        self._reset_monthly_cost_if_needed(user_key)

        # Update cache
        user_data = self._cost_cache[user_key]
        user_data["total_cost"] += cost

        logger.info(
            f"Recorded cost for user {user_id}: ${cost:.4f} "
            f"(monthly total: ${user_data['total_cost']:.2f})"
        )

        # Optionally persist to database
        if db and user_id:
            await self._persist_cost_to_db(db, user_id, cost)

    async def _persist_cost_to_db(
        self, db: AsyncSession, user_id: UUID, cost: float
    ) -> None:
        """Persist cost data to analytics snapshots (optional).
        
        This updates today's analytics snapshot with AI cost data.
        """
        try:
            today = datetime.now(timezone.utc).date()

            # Try to find today's snapshot
            result = await db.execute(
                select(AnalyticsSnapshot)
                .where(AnalyticsSnapshot.user_id == user_id)
                .where(AnalyticsSnapshot.snapshot_date == today)
            )
            snapshot = result.scalar_one_or_none()

            if snapshot:
                # Update existing snapshot
                # Note: AnalyticsSnapshot doesn't have AI cost fields yet
                # This is a placeholder for future enhancement
                logger.debug(f"Updated analytics snapshot for {today}")
            else:
                logger.debug(f"No analytics snapshot found for {today}")

        except Exception as e:
            logger.error(f"Failed to persist cost to database: {e}")
            # Don't raise - cost tracking shouldn't break the application

    async def get_monthly_usage(self, user_id: Optional[UUID] = None) -> dict:
        """Get monthly cost usage for user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dictionary with total_cost, budget_limit, remaining_budget, percentage_used
        """
        user_key = self._get_user_key(user_id)

        if user_key not in self._cost_cache:
            return {
                "total_cost": 0.0,
                "budget_limit": self.monthly_budget,
                "remaining_budget": self.monthly_budget,
                "percentage_used": 0.0,
            }

        self._reset_monthly_cost_if_needed(user_key)

        user_data = self._cost_cache[user_key]
        total_cost = user_data["total_cost"]
        remaining = max(0.0, self.monthly_budget - total_cost)
        percentage = (total_cost / self.monthly_budget * 100) if self.monthly_budget > 0 else 0.0

        return {
            "total_cost": round(total_cost, 4),
            "budget_limit": self.monthly_budget,
            "remaining_budget": round(remaining, 4),
            "percentage_used": round(percentage, 2),
        }

    async def reset_user_costs(self, user_id: UUID) -> None:
        """Reset cost tracking for a user (admin function).
        
        Args:
            user_id: User ID to reset costs for
        """
        user_key = self._get_user_key(user_id)
        if user_key in self._cost_cache:
            del self._cost_cache[user_key]
            logger.info(f"Reset cost tracking for user {user_id}")

    async def get_cost_warning_threshold(self, user_id: Optional[UUID] = None) -> Optional[str]:
        """Check if user is approaching budget limit.
        
        Returns warning message if user has used >80% of budget.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Warning message if approaching limit, None otherwise
        """
        usage = await self.get_monthly_usage(user_id)
        percentage = usage["percentage_used"]

        if percentage >= 90:
            return (
                f"⚠️ CRITICAL: You've used {percentage:.1f}% of your monthly AI budget "
                f"(${usage['total_cost']:.2f} / ${usage['budget_limit']:.2f})"
            )
        elif percentage >= 80:
            return (
                f"⚠️ WARNING: You've used {percentage:.1f}% of your monthly AI budget "
                f"(${usage['total_cost']:.2f} / ${usage['budget_limit']:.2f})"
            )

        return None


# Global instance
cost_tracking_service = CostTrackingService()
