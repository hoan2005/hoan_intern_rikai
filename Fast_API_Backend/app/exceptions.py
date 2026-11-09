import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.response_format import error_envelope

logger = logging.getLogger("app")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = error["loc"][-1]
            message = error["msg"]
            if message.startswith("Value error"):
                message = message.replace("Value error, ", "")
            errors.append({"field": field, "message": message})
        logger.warning(
            "Request validation failed: %s %s fields=%s",
            request.method,
            request.url.path,
            [error["field"] for error in errors],
        )
        message = "; ".join(
            f"{error['field']}: {error['message']}" for error in errors
        )
        return JSONResponse(
            status_code=422,
            content=error_envelope(message or "Request validation failed"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        message = (
            exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_envelope(message),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception for %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content=error_envelope("Internal Server Error"),
        )
