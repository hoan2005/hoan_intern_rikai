from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.dependencies import get_db
from app.models.post_models import Post
from app.repositories.post_repo import get_all_posts
from app.routers import post_routers
from app.services import post_service


def _create_test_client() -> TestClient:
    test_app = FastAPI()
    test_app.include_router(post_routers.router)
    test_app.dependency_overrides[get_db] = lambda: object()
    return TestClient(test_app)


def test_search_returns_paginated_posts_without_sort_parameter(
    monkeypatch,
) -> None:
    paginated_posts = {
        "page": 2,
        "limit": 1,
        "total": 3,
        "items": [
            {
                "id": 1,
                "title": "FastAPI",
                "content": "Search example",
                "user_id": 1,
                "category": None,
                "published": True,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            }
        ],
    }
    get_all = Mock(return_value=paginated_posts)
    monkeypatch.setattr(post_service, "get_all_posts", get_all)

    response = _create_test_client().get(
        "/posts",
        params={"search": "fastapi", "page": 2, "limit": 1},
    )

    assert response.status_code == 200
    assert response.json()["page"] == 2
    assert response.json()["limit"] == 1
    assert response.json()["total"] == 3
    assert response.json()["items"][0]["title"] == "FastAPI"
    get_all.assert_called_once()
    assert get_all.call_args.args[-1] == "fastapi"


def test_posts_without_search_are_paginated(monkeypatch) -> None:
    paginated_posts = {
        "page": 1,
        "limit": 10,
        "total": 0,
        "items": [],
    }
    monkeypatch.setattr(
        post_service, "get_all_posts", lambda *args: paginated_posts
    )

    response = _create_test_client().get("/posts")

    assert response.status_code == 200
    assert response.json() == paginated_posts


def test_repository_searches_and_paginates_in_created_at_order() -> None:
    posts = [Mock(spec=Post)]
    query = Mock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.count.return_value = 3
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = posts
    db = Mock()
    db.query.return_value = query

    result = get_all_posts(db, page=2, limit=1, search="fastapi")

    assert result == {"page": 2, "limit": 1, "total": 3, "items": posts}
    search_expression = query.filter.call_args.args[0]
    search_sql = str(search_expression.compile(dialect=postgresql.dialect()))
    assert "post.title ILIKE" in search_sql
    assert "post.content ILIKE" in search_sql
    query.order_by.assert_called_once_with(Post.created_at, Post.id)
    query.offset.assert_called_once_with(1)
    query.limit.assert_called_once_with(1)
