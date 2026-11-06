import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger("app")

_INCREMENT_AND_SET_EXPIRY = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return {count, redis.call('TTL', KEYS[1])}
"""


def register_rate_limiting(app: FastAPI) -> None:
    @app.middleware("http")
    async def enforce_rate_limit(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate-limit:{client_ip}"
        redis_client: Redis = request.app.state.redis

        try:
            count, ttl = await redis_client.eval(
                _INCREMENT_AND_SET_EXPIRY,
                1,
                key,
                settings.RATE_LIMIT_WINDOW_SECONDS,
            )
        except RedisError:
            logger.exception(
                "Rate limit check failed for client %s", client_ip
            )
            return JSONResponse(
                status_code=503,
                content={"detail": "Rate limiting service unavailable"},
            )

        if count > settings.RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(max(1, ttl))},
            )

        return await call_next(request)
