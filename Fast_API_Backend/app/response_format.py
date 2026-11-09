import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response


def success_envelope(data: Any) -> dict[str, Any]:
    return {"success": True, "message": "Success", "data": data}


def error_envelope(message: str) -> dict[str, Any]:
    return {"success": False, "message": message}


def register_global_response_format(app: FastAPI) -> None:
    @app.middleware("http")
    async def format_response(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in {
            "/docs",
            "/docs/oauth2-redirect",
            "/openapi.json",
            "/redoc",
        }:
            return await call_next(request)

        response = await call_next(request)
        if 300 <= response.status_code < 400:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        try:
            payload = json.loads(body) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = body.decode("utf-8", errors="replace")

        if isinstance(payload, dict) and isinstance(
            payload.get("success"), bool
        ):
            envelope = payload
        elif response.status_code >= 400:
            message = (
                payload.get("detail", "Request failed")
                if isinstance(payload, dict)
                else payload
            )
            envelope = error_envelope(
                message if isinstance(message, str) else json.dumps(message)
            )
        else:
            envelope = success_envelope({} if payload is None else payload)

        headers = {
            name: value
            for name, value in response.headers.items()
            if name.lower()
            not in {"content-length", "content-type", "transfer-encoding"}
        }
        status_code = (
            200 if response.status_code == 204 else response.status_code
        )
        return JSONResponse(
            content=envelope,
            status_code=status_code,
            headers=headers,
        )
