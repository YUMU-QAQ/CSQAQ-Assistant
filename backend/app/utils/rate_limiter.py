"""Token-bucket rate limiter for CSQAQ API (1 req/sec)."""
import asyncio
import time
from typing import Optional


class TokenBucket:
    """Simple token-bucket rate limiter."""

    def __init__(self, rate: float = 1.0, burst: int = 3):
        """
        Args:
            rate: Tokens per second.
            burst: Maximum burst size.
        """
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Wait until a token is available, then consume it."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
                self.last_refill = time.monotonic()
            else:
                self.tokens -= 1.0


# Singleton rate limiter for CSQAQ API
_rate_limiter: Optional[TokenBucket] = None


def get_rate_limiter(rate: float = 1.0) -> TokenBucket:
    """Get or create the singleton rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = TokenBucket(rate=rate)
    return _rate_limiter
