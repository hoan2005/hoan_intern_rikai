import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.main import app
from app.models.user_model import User


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        email="user@gmail.com",
        full_name="Người dùng",
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_current_user_profile(client):
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "user@gmail.com",
        "full_name": "Người dùng",
    }
    assert "password_hash" not in response.json()
