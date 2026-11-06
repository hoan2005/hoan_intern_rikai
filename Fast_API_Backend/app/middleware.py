from collections.abc import Awaitable, Callable
import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.core.logging_config import configure_logging


def register_request_logging(app: FastAPI) -> None:
    logger: logging.Logger = configure_logging()

    @app.middleware("http")
    async def log_requests(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        method = request.method
        path = request.url.path
        logger.info("Request started: %s %s", method, path)
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Request failed with status 500: %s %s", method, path
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "Request completed: %s %s status=%s duration_ms=%.2f",
            method,
            path,
            response.status_code,
            duration_ms,
        )
        return response
