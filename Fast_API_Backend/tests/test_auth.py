from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import dependencies
from app.dependencies import get_db
from app.routers import auth_routers, post_routers, user_routers
from app.services import auth_service, post_service, user_service
from app.services.user_service import _hash_password


def _create_test_client() -> TestClient:
    test_app = FastAPI()
    test_app.include_router(auth_routers.router)
    test_app.include_router(post_routers.router)
    test_app.include_router(user_routers.router)
    test_app.dependency_overrides[get_db] = lambda: object()
    return TestClient(test_app)


def test_login_returns_bearer_access_token(monkeypatch) -> None:
    monkeypatch.setattr(auth_service, "authenticate_user", lambda *args: 7)
    monkeypatch.setattr(
        auth_service, "create_access_token", lambda user_id: "signed-token"
    )

    response = _create_test_client().post(
        "/login", data={"username": "testuser", "password": "secret"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "signed-token",
        "token_type": "bearer",
    }


def test_login_rejects_invalid_credentials(monkeypatch) -> None:
    monkeypatch.setattr(auth_service, "authenticate_user", lambda *args: None)

    response = _create_test_client().post(
        "/login", data={"username": "testuser", "password": "wrong"}
    )

    assert response.status_code == 401


def test_authenticate_user_verifies_stored_password(monkeypatch) -> None:
    monkeypatch.setattr(auth_service.settings, "SCRYPT_N", 8192)
    monkeypatch.setattr(auth_service.settings, "SCRYPT_R", 8)
    monkeypatch.setattr(auth_service.settings, "SCRYPT_P", 1)
    password_hash = _hash_password("correct-password")
    assert password_hash.startswith("scrypt$8192$8$1$")
    user = Mock(id=7, hashed_password=password_hash)
    monkeypatch.setattr(
        auth_service.user_repo,
        "get_user_by_username_or_email",
        lambda db, username: user,
    )

    assert (
        auth_service.authenticate_user(Mock(), "testuser", "correct-password")
        == 7
    )
    assert (
        auth_service.authenticate_user(Mock(), "testuser", "wrong-password")
        is None
    )


def test_access_token_dependency_returns_user_id(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: Mock(id=user_id),
    )

    token = auth_service.create_access_token(7)

    assert dependencies.get_current_user_id(token, Mock()) == 7


def test_post_mutations_require_owner_or_admin(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(id=7, role="user")
    post = SimpleNamespace(id=1, user_id=8, published=False)
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    monkeypatch.setattr(
        post_service.post_repo, "get_post_by_id", lambda db, post_id: post
    )
    update_post = Mock()
    delete_post = Mock()
    monkeypatch.setattr(post_service.post_repo, "update_post", update_post)
    monkeypatch.setattr(post_service.post_repo, "delete_post", delete_post)
    token = auth_service.create_access_token(7)
    client = _create_test_client()
    headers = {"Authorization": f"Bearer {token}"}

    update_response = client.put(
        "/posts/1", json={"title": "Updated"}, headers=headers
    )
    delete_response = client.delete("/posts/1", headers=headers)

    assert update_response.status_code == 403
    assert delete_response.status_code == 403
    update_post.assert_not_called()
    delete_post.assert_not_called()


def test_admin_can_manage_another_users_post(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(id=7, role="admin")
    post = SimpleNamespace(id=1, user_id=8, published=False)
    post_response = {
        "id": 1,
        "title": "Title",
        "content": "Content",
        "user_id": 8,
        "category": None,
        "published": False,
        "created_at": "2026-01-01T00:00:00Z",
    }
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    monkeypatch.setattr(
        post_service.post_repo, "get_post_by_id", lambda db, post_id: post
    )
    update_post = Mock(return_value=post_response)
    delete_post = Mock()
    monkeypatch.setattr(post_service.post_repo, "update_post", update_post)
    monkeypatch.setattr(post_service.post_repo, "delete_post", delete_post)
    token = auth_service.create_access_token(7)
    client = _create_test_client()
    headers = {"Authorization": f"Bearer {token}"}

    update_response = client.put(
        "/posts/1", json={"title": "Updated"}, headers=headers
    )
    delete_response = client.delete("/posts/1", headers=headers)

    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    update_post.assert_called_once()
    delete_post.assert_called_once()
    assert len(update_post.call_args.args) == 3
    assert update_post.call_args.args[1] is post
    assert len(delete_post.call_args.args) == 2
    assert delete_post.call_args.args[1] is post


def test_private_post_is_hidden_from_anonymous_and_other_users(
    monkeypatch,
) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    owner = SimpleNamespace(id=8, role="user")
    other_user = SimpleNamespace(id=7, role="user")
    post = SimpleNamespace(
        id=1,
        user_id=8,
        published=False,
        title="Title",
        content="Content",
        category=None,
        created_at="2026-01-01T00:00:00Z",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: owner if user_id == 8 else other_user,
    )
    get_post = Mock(return_value=post)
    monkeypatch.setattr(post_service.post_repo, "get_post_by_id", get_post)
    client = _create_test_client()

    assert client.get("/posts/1").status_code == 404
    other_token = auth_service.create_access_token(7)
    assert (
        client.get(
            "/posts/1",
            headers={"Authorization": f"Bearer {other_token}"},
        ).status_code
        == 404
    )
    owner_token = auth_service.create_access_token(8)
    assert (
        client.get(
            "/posts/1",
            headers={"Authorization": f"Bearer {owner_token}"},
        ).status_code
        == 200
    )
    assert get_post.call_count == 3
    assert all(
        len(call.args) == 2 and call.args[1] == 1
        for call in get_post.call_args_list
    )


def test_user_cannot_promote_self_to_admin(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(
        id=7,
        username="testuser",
        email="test1@gmail.com",
        role="user",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    token = auth_service.create_access_token(7)

    response = _create_test_client().put(
        "/users/7",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_profile_requires_token_and_returns_user_with_valid_token(
    monkeypatch,
) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(
        id=7,
        username="testuser",
        email="test1@gmail.com",
        role="user",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    token = auth_service.create_access_token(7)
    client = _create_test_client()

    assert client.get("/profile").status_code == 401
    response = client.get(
        "/profile", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["role"] == "user"


def test_user_list_requires_login_but_not_admin(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(
        id=7,
        username="testuser",
        email="test1@gmail.com",
        role="user",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    monkeypatch.setattr(user_service, "get_all_users", lambda db: [])
    client = _create_test_client()
    token = auth_service.create_access_token(7)

    assert client.get("/users").status_code == 401
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_create_user_requires_admin_and_created_role_is_user(
    monkeypatch,
) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(
        id=7,
        username="adminuser",
        email="admin1@gmail.com",
        role="admin",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    created_user = {
        "id": 8,
        "username": "newuser",
        "email": "newuser1@gmail.com",
        "role": "user",
    }
    create_user = Mock(return_value=created_user)
    monkeypatch.setattr(user_service, "create_user", create_user)
    client = _create_test_client()
    payload = {
        "username": "newuser",
        "email": "newuser1@gmail.com",
        "password": "secret123",
    }

    assert client.post("/users", json=payload).status_code == 401

    token = auth_service.create_access_token(7)
    response = client.post(
        "/users",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"
    create_user.assert_called_once()


def test_regular_user_cannot_create_user(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    current_user = SimpleNamespace(
        id=7,
        username="testuser",
        email="test1@gmail.com",
        role="user",
    )
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: current_user,
    )
    token = auth_service.create_access_token(7)

    response = _create_test_client().post(
        "/users",
        json={
            "username": "newuser",
            "email": "newuser1@gmail.com",
            "password": "secret123",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_write_endpoint_requires_a_valid_token(monkeypatch) -> None:
    secret = "a-secure-test-secret-that-is-long-enough"
    monkeypatch.setattr(dependencies.settings, "JWT_SECRET_KEY", secret)
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: Mock(id=user_id),
    )
    created_post = {
        "id": 1,
        "title": "Title",
        "content": "Content",
        "user_id": 7,
        "category": None,
        "published": False,
        "created_at": "2026-01-01T00:00:00Z",
    }
    create_post = Mock(return_value=created_post)
    monkeypatch.setattr(post_service, "create_post", create_post)

    client = _create_test_client()
    post_data = {
        "title": "Title",
        "content": "Content",
    }

    assert client.post("/posts", json=post_data).status_code == 401

    token = jwt.encode(
        {"sub": "7", "exp": 4_102_444_800},
        secret,
        algorithm="HS256",
    )
    response = client.post(
        "/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["user_id"] == 7
    create_post.assert_called_once()
    assert create_post.call_args.args[2] == 7


@pytest.mark.parametrize("token", ["not-a-jwt", ""])
def test_invalid_token_is_rejected(monkeypatch, token: str) -> None:
    monkeypatch.setattr(
        dependencies.settings,
        "JWT_SECRET_KEY",
        "a-secure-test-secret-that-is-long-enough",
    )
    monkeypatch.setattr(
        dependencies.user_repo,
        "get_user_by_id",
        lambda db, user_id: Mock(id=user_id),
    )
    token = token or " "

    response = _create_test_client().put(
        "/users/7",
        json={"username": "newname"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
