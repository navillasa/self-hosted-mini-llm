from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import HTTPException
from config import settings


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        # Store timestamps of requests per user
        self.request_log: Dict[str, List[datetime]] = defaultdict(list)

    def check_rate_limit(self, user_id: str) -> dict:
        """
        Check if user has exceeded rate limits.
        Returns usage stats if allowed, raises HTTPException if rate limited.
        """
        now = datetime.utcnow()
        user_requests = self.request_log[user_id]

        # Clean up old requests (older than 24 hours)
        cutoff_daily = now - timedelta(days=1)
        user_requests[:] = [ts for ts in user_requests if ts > cutoff_daily]

        # Check per-minute rate limit
        cutoff_minute = now - timedelta(minutes=1)
        requests_last_minute = sum(1 for ts in user_requests if ts > cutoff_minute)

        if requests_last_minute >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit_type": "per_minute",
                    "limit": settings.rate_limit_per_minute,
                    "retry_after_seconds": 60
                }
            )

        # Check daily rate limit
        requests_today = len(user_requests)

        if requests_today >= settings.rate_limit_per_day:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Daily rate limit exceeded",
                    "limit_type": "per_day",
                    "limit": settings.rate_limit_per_day,
                    "retry_after_seconds": int((cutoff_daily + timedelta(days=1) - now).total_seconds())
                }
            )

        # Log this request
        user_requests.append(now)

        # Return usage stats
        return {
            "requests_last_minute": requests_last_minute + 1,
            "requests_today": requests_today + 1,
            "limit_per_minute": settings.rate_limit_per_minute,
            "limit_per_day": settings.rate_limit_per_day,
            "remaining_minute": settings.rate_limit_per_minute - requests_last_minute - 1,
            "remaining_day": settings.rate_limit_per_day - requests_today - 1,
        }

    def get_usage_stats(self, user_id: str) -> dict:
        """Get current usage stats without logging a request"""
        now = datetime.utcnow()
        user_requests = self.request_log[user_id]

        # Clean up old requests
        cutoff_daily = now - timedelta(days=1)
        user_requests[:] = [ts for ts in user_requests if ts > cutoff_daily]

        # Count requests
        cutoff_minute = now - timedelta(minutes=1)
        requests_last_minute = sum(1 for ts in user_requests if ts > cutoff_minute)
        requests_today = len(user_requests)

        return {
            "requests_last_minute": requests_last_minute,
            "requests_today": requests_today,
            "limit_per_minute": settings.rate_limit_per_minute,
            "limit_per_day": settings.rate_limit_per_day,
            "remaining_minute": settings.rate_limit_per_minute - requests_last_minute,
            "remaining_day": settings.rate_limit_per_day - requests_today,
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
