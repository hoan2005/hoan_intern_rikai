import logging

from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.schemas.post_schemas import PaginatedPostResponse

logger = logging.getLogger("app")

POSTS_CACHE_TTL_SECONDS = 60
POSTS_CACHE_PATTERN = "posts:page=*:limit=*"


def posts_cache_key(page: int, limit: int) -> str:
    return f"posts:page={page}:limit={limit}"


async def get_cached_posts(
    redis_client: Redis, page: int, limit: int
) -> PaginatedPostResponse | None:
    key = posts_cache_key(page, limit)
    try:
        cached_posts = await redis_client.get(key)
    except RedisError:
        logger.exception("Could not read posts cache for key %s", key)
        return None

    if cached_posts is None:
        return None

    try:
        return PaginatedPostResponse.model_validate_json(cached_posts)
    except (ValidationError, ValueError):
        logger.warning("Invalid posts cache entry for key %s", key)
        try:
            await redis_client.delete(key)
        except RedisError:
            logger.exception(
                "Could not delete invalid posts cache key %s", key
            )
        return None


async def set_cached_posts(
    redis_client: Redis,
    page: int,
    limit: int,
    posts: dict[str, object],
) -> None:
    key = posts_cache_key(page, limit)
    response = PaginatedPostResponse.model_validate(posts)
    try:
        await redis_client.set(
            key,
            response.model_dump_json(),
            ex=POSTS_CACHE_TTL_SECONDS,
        )
    except RedisError:
        logger.exception("Could not write posts cache for key %s", key)


async def invalidate_posts_cache(redis_client: Redis) -> None:
    try:
        keys = [
            key
            async for key in redis_client.scan_iter(match=POSTS_CACHE_PATTERN)
        ]
        if keys:
            await redis_client.delete(*keys)
    except RedisError:
        logger.exception("Could not invalidate posts cache")
