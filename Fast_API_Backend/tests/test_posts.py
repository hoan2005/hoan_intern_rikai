from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
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
        post_service,
        "get_all_posts",
        lambda *args, **kwargs: paginated_posts,
    )

    response = _create_test_client().get("/posts")

    assert response.status_code == 200
    assert response.json() == paginated_posts


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"limit": 0},
        {"limit": 101},
        {"author_id": 0},
        {"category": ""},
        {"category": "a" * 101},
        {"search": ""},
    ],
)
def test_list_posts_validates_filters_in_service(params) -> None:
    response = _create_test_client().get("/posts", params=params)

    assert response.status_code == 422


def test_service_passes_current_user_role_to_repository(monkeypatch) -> None:
    paginated_posts = {"page": 1, "limit": 10, "total": 0, "items": []}
    get_all = Mock(return_value=paginated_posts)
    monkeypatch.setattr(post_service.post_repo, "get_all_posts", get_all)
    db = Mock()

    result = post_service.get_all_posts(
        db, current_user_id=7, current_user_role="admin"
    )

    assert result == paginated_posts
    get_all.assert_called_once_with(
        db,
        1,
        10,
        None,
        None,
        None,
        None,
        current_user_id=7,
        is_admin=True,
    )


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


def test_repository_hides_unpublished_posts_from_anonymous_users() -> None:
    query = Mock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.count.return_value = 0
    query.offset.return_value = query
    query.limit.return_value = query
    query.all.return_value = []
    db = Mock()
    db.query.return_value = query

    get_all_posts(db, page=1, limit=10)

    filters = [
        str(call.args[0].compile(dialect=postgresql.dialect()))
        for call in query.filter.call_args_list
    ]
    assert any("published IS true" in expression for expression in filters)


def test_repository_allows_own_drafts_for_user_and_all_posts_for_admin() -> (
    None
):
    def create_db():
        query = Mock()
        query.filter.return_value = query
        query.order_by.return_value = query
        query.count.return_value = 0
        query.offset.return_value = query
        query.limit.return_value = query
        query.all.return_value = []
        db = Mock()
        db.query.return_value = query
        return db, query

    user_db, user_query = create_db()
    get_all_posts(
        user_db,
        page=1,
        limit=10,
        current_user_id=7,
    )
    user_filters = [
        str(
            call.args[0].compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )
        for call in user_query.filter.call_args_list
    ]
    assert any(
        "published IS true" in expression and "user_id = 7" in expression
        for expression in user_filters
    )

    admin_db, admin_query = create_db()
    get_all_posts(
        admin_db,
        page=1,
        limit=10,
        current_user_id=7,
        is_admin=True,
    )
    admin_query.filter.assert_not_called()
