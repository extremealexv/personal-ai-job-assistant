"""Rate limiting service for AI API calls."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from app.config import settings
from app.core.ai_exceptions import RateLimitError

logger = logging.getLogger(__name__)


class RateLimitService:
    """Service for managing rate limits on AI API calls.
    
    This implementation uses in-memory storage. For production with multiple
    workers, use Redis with the RedisRateLimitService implementation.
    """

    def __init__(self):
        """Initialize rate limit service."""
        # In-memory storage: user_id -> {requests: [...timestamps], daily_requests: count, day: date}
        self._rate_limits: dict[str, dict] = {}
        self.requests_per_minute = settings.ai_requests_per_minute
        self.requests_per_day = settings.ai_requests_per_day

    def _get_user_key(self, user_id: Optional[UUID]) -> str:
        """Get cache key for user."""
        return str(user_id) if user_id else "anonymous"

    def _cleanup_old_requests(self, user_key: str) -> None:
        """Remove requests older than 1 minute."""
        if user_key not in self._rate_limits:
            return

        now = datetime.now(timezone.utc)
        one_minute_ago = now - timedelta(minutes=1)

        user_data = self._rate_limits[user_key]
        user_data["requests"] = [
            ts for ts in user_data.get("requests", []) if ts > one_minute_ago
        ]

    def _reset_daily_counter_if_needed(self, user_key: str) -> None:
        """Reset daily counter if it's a new day."""
        if user_key not in self._rate_limits:
            return

        today = datetime.now(timezone.utc).date()
        user_data = self._rate_limits[user_key]

        if user_data.get("day") != today:
            user_data["daily_requests"] = 0
            user_data["day"] = today

    async def check_rate_limit(self, user_id: Optional[UUID] = None) -> None:
        """Check if user has exceeded rate limits.
        
        Args:
            user_id: User ID to check limits for
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        user_key = self._get_user_key(user_id)

        # Initialize user data if needed
        if user_key not in self._rate_limits:
            self._rate_limits[user_key] = {
                "requests": [],
                "daily_requests": 0,
                "day": datetime.now(timezone.utc).date(),
            }

        # Clean up old requests
        self._cleanup_old_requests(user_key)
        self._reset_daily_counter_if_needed(user_key)

        user_data = self._rate_limits[user_key]

        # Check per-minute limit
        current_minute_requests = len(user_data["requests"])
        if current_minute_requests >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded (per-minute) for user {user_id}: "
                f"{current_minute_requests}/{self.requests_per_minute}"
            )
            raise RateLimitError(
                f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                retry_after=60,
            )

        # Check per-day limit
        if user_data["daily_requests"] >= self.requests_per_day:
            logger.warning(
                f"Rate limit exceeded (daily) for user {user_id}: "
                f"{user_data['daily_requests']}/{self.requests_per_day}"
            )
            # Calculate seconds until midnight
            now = datetime.now(timezone.utc)
            midnight = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            retry_after = int((midnight - now).total_seconds())

            raise RateLimitError(
                f"Daily rate limit exceeded: {self.requests_per_day} requests per day",
                retry_after=retry_after,
            )

    async def record_request(self, user_id: Optional[UUID] = None) -> None:
        """Record a successful API request.
        
        Args:
            user_id: User ID to record request for
        """
        user_key = self._get_user_key(user_id)

        if user_key not in self._rate_limits:
            self._rate_limits[user_key] = {
                "requests": [],
                "daily_requests": 0,
                "day": datetime.now(timezone.utc).date(),
            }

        now = datetime.now(timezone.utc)
        user_data = self._rate_limits[user_key]

        # Add timestamp for per-minute tracking
        user_data["requests"].append(now)

        # Increment daily counter
        user_data["daily_requests"] += 1

        logger.debug(
            f"Recorded request for user {user_id}: "
            f"minute={len(user_data['requests'])}/{self.requests_per_minute}, "
            f"day={user_data['daily_requests']}/{self.requests_per_day}"
        )

    async def get_remaining_requests(
        self, user_id: Optional[UUID] = None
    ) -> dict[str, int]:
        """Get remaining requests for user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dictionary with remaining_minute and remaining_day
        """
        user_key = self._get_user_key(user_id)

        if user_key not in self._rate_limits:
            return {
                "remaining_minute": self.requests_per_minute,
                "remaining_day": self.requests_per_day,
            }

        self._cleanup_old_requests(user_key)
        self._reset_daily_counter_if_needed(user_key)

        user_data = self._rate_limits[user_key]

        return {
            "remaining_minute": self.requests_per_minute - len(user_data["requests"]),
            "remaining_day": self.requests_per_day - user_data["daily_requests"],
        }

    async def reset_user_limits(self, user_id: UUID) -> None:
        """Reset rate limits for a user (admin function).
        
        Args:
            user_id: User ID to reset limits for
        """
        user_key = self._get_user_key(user_id)
        if user_key in self._rate_limits:
            del self._rate_limits[user_key]
            logger.info(f"Reset rate limits for user {user_id}")


# Global instance
rate_limit_service = RateLimitService()
