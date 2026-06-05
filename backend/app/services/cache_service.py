"""In-memory TTL cache for API responses."""
from __future__ import annotations
import time
import asyncio
from typing import Any, Optional


class TTLCache:
    """Simple in-memory cache with TTL."""

    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)

    def get(self, key: str) -> Optional[Any]:
        """Get a value if not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 60):
        """Set a value with TTL."""
        self._cache[key] = (value, time.monotonic() + ttl_seconds)

    def delete(self, key: str):
        """Remove a key."""
        self._cache.pop(key, None)

    def clear(self):
        """Clear all entries."""
        self._cache.clear()

    async def cleanup_expired(self):
        """Periodic cleanup of expired entries."""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            now = time.monotonic()
            expired = [k for k, (_, exp) in self._cache.items() if now > exp]
            for k in expired:
                del self._cache[k]


# Singleton cache
cache = TTLCache()
