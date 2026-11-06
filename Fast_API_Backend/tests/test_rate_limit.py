from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from redis.exceptions import RedisError

from app import rate_limit


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    async def eval(
        self, script: str, number_of_keys: int, key: str, window: int
    ) -> list[int]:
        assert number_of_keys == 1
        assert window == rate_limit.settings.RATE_LIMIT_WINDOW_SECONDS
        count = self.counts.get(key, 0) + 1
        self.counts[key] = count
        return [count, window]


def _create_test_app(redis_client: FakeRedis | None = None) -> FastAPI:
    test_app = FastAPI()
    test_app.state.redis = redis_client or FakeRedis()
    rate_limit.register_rate_limiting(test_app)

    @test_app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "ok"}

    return test_app


def test_rate_limit_returns_429_after_configured_request_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rate_limit.settings, "RATE_LIMIT_REQUESTS", 2)
    client = TestClient(_create_test_app())

    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 200
    response = client.get("/")

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}
    assert response.headers["Retry-After"] == "60"


def test_rate_limit_counts_requests_per_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rate_limit.settings, "RATE_LIMIT_REQUESTS", 1)
    app = _create_test_app()

    first_client = TestClient(app, client=("192.0.2.1", 1000))
    second_client = TestClient(app, client=("192.0.2.2", 1000))

    assert first_client.get("/").status_code == 200
    assert first_client.get("/").status_code == 429
    assert second_client.get("/").status_code == 200


def test_rate_limit_returns_503_if_redis_is_unavailable(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class UnavailableRedis:
        async def eval(
            self, script: str, number_of_keys: int, key: str, window: int
        ) -> list[int]:
            raise RedisError("Redis unavailable")

    response = TestClient(_create_test_app(UnavailableRedis())).get("/")

    assert response.status_code == 503
    assert response.json() == {"detail": "Rate limiting service unavailable"}
    assert "Rate limit check failed" in caplog.text
