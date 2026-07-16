import time
from collections import defaultdict
from threading import Lock

from fastapi import Header, HTTPException, Request

from .config import get_settings


def require_ops_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != get_settings().ops_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = [t for t in self._hits[key] if now - t < self._window]
            if len(hits) >= self._max:
                self._hits[key] = hits
                return False
            hits.append(now)
            self._hits[key] = hits
            return True


_limiter = RateLimiter(max_requests=30, window_seconds=60.0)


async def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not _limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests, slow down.")
