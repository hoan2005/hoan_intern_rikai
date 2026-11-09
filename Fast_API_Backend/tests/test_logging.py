import logging
from collections.abc import Generator
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

from app import middleware
from app.core import logging_config
from app.exceptions import register_exception_handlers
from app.response_format import register_global_response_format


@pytest.fixture
def log_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Path, None, None]:
    path = tmp_path / "app.log"
    monkeypatch.setattr(logging_config, "LOG_FILE", path)
    yield path

    logger = logging.getLogger("app")
    for handler in logger.handlers[:]:
        if (
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename) == path
        ):
            logger.removeHandler(handler)
            handler.close()


def _create_test_app() -> FastAPI:
    test_app = FastAPI()
    middleware.register_request_logging(test_app)
    register_global_response_format(test_app)
    register_exception_handlers(test_app)

    @test_app.get("/ok")
    async def ok() -> dict[str, bool]:
        return {"ok": True}

    @test_app.get("/error")
    async def error() -> None:
        raise RuntimeError("expected test error")

    @test_app.get("/items/{item_id}")
    async def item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @test_app.get("/http-error")
    async def http_error() -> None:
        raise HTTPException(status_code=404, detail="Not found")

    @test_app.get("/empty")
    async def empty() -> None:
        return None

    @test_app.delete("/no-content", status_code=204)
    async def no_content() -> None:
        return None

    return test_app


def test_logs_request_and_response(
    log_file: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = _create_test_app()

    with caplog.at_level(logging.INFO, logger="app"):
        response = TestClient(app).get("/ok")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Success",
        "data": {"ok": True},
    }
    assert "Request started: GET /ok" in caplog.text
    assert "Request completed: GET /ok status=200" in caplog.text
    assert "Request completed: GET /ok status=200" in log_file.read_text()


def test_logs_unhandled_exception(
    log_file: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = _create_test_app()

    with caplog.at_level(logging.ERROR, logger="app"):
        response = TestClient(app, raise_server_exceptions=False).get("/error")

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "message": "Internal Server Error",
    }
    assert "Request failed with status 500: GET /error" in caplog.text
    assert "expected test error" in log_file.read_text()


def test_logs_validation_exception_without_request_values(
    log_file: Path, caplog: pytest.LogCaptureFixture
) -> None:
    app = _create_test_app()

    with caplog.at_level(logging.INFO, logger="app"):
        response = TestClient(app).get("/items/not-an-integer")

    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "message": (
            "item_id: Input should be a valid integer, "
            "unable to parse string as an integer"
        ),
    }
    assert (
        "Request validation failed: GET /items/not-an-integer" in caplog.text
    )
    assert (
        "Request completed: GET /items/not-an-integer status=422"
        in log_file.read_text()
    )


def test_http_errors_use_standard_error_envelope() -> None:
    response = TestClient(_create_test_app()).get("/http-error")

    assert response.status_code == 404
    assert response.json() == {"success": False, "message": "Not found"}


def test_empty_success_response_uses_standard_success_envelope() -> None:
    response = TestClient(_create_test_app()).get("/empty")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Success",
        "data": {},
    }


def test_no_content_success_is_converted_to_standard_envelope() -> None:
    response = TestClient(_create_test_app()).delete("/no-content")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Success",
        "data": {},
    }
