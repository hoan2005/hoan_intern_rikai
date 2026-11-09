from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.user_models import User
from app.repositories.user_repo import get_users_with_posts
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services import user_service


def test_create_user_accepts_valid_data() -> None:
    user = UserCreate(
        username="testuser",
        email="user123@gmail.com",
        password="secret123",
    )

    assert user.username == "testuser"
    assert str(user.email) == "user123@gmail.com"
    assert not hasattr(user, "role")


def test_create_user_rejects_role_override() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="user123@gmail.com",
            password="secret123",
            role="admin",
        )


def test_create_user_rejects_short_username() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="user123@gmail.com",
            password="secret123",
        )


def test_update_user_accepts_partial_data() -> None:
    user = UserUpdate(username="newusername")

    assert user.username == "newusername"
    assert user.email is None
    assert user.password is None


def test_get_users_with_posts_uses_joinedload_and_single_query() -> None:
    query = Mock()
    query.options.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    users = [Mock(spec=User), Mock(spec=User)]
    query.all.return_value = users
    db = Mock()
    db.query.return_value = query

    result = get_users_with_posts(db, [7, 8], current_user_id=7)

    assert result == users
    db.query.assert_called_once_with(User)
    query.all.assert_called_once()

    joined_statement = (
        select(User)
        .options(*query.options.call_args.args)
        .where(User.id.in_([7, 8]))
        .order_by(User.id)
    )
    compiled = str(
        joined_statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
    assert "LEFT OUTER JOIN post.post AS post_1" in compiled
    assert "post_1.published IS true" in compiled
    assert "post_1.user_id = 7" in compiled


def test_anonymous_query_only_eager_loads_public_posts() -> None:
    query = Mock()
    query.options.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = []
    db = Mock()
    db.query.return_value = query

    get_users_with_posts(db, [7, 8], current_user_id=None)

    joined_statement = (
        select(User)
        .options(*query.options.call_args.args)
        .where(User.id.in_([7, 8]))
        .order_by(User.id)
    )
    compiled = str(
        joined_statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
    assert "LEFT OUTER JOIN post.post AS post_1" in compiled
    assert "post_1.published IS true" in compiled
    assert "post_1.user_id =" not in compiled


def test_admin_query_eager_loads_public_and_unpublished_posts() -> None:
    query = Mock()
    query.options.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = []
    db = Mock()
    db.query.return_value = query

    get_users_with_posts(db, [7, 8], current_user_id=7, is_admin=True)

    joined_statement = (
        select(User)
        .options(*query.options.call_args.args)
        .where(User.id.in_([7, 8]))
        .order_by(User.id)
    )
    compiled = str(
        joined_statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )
    assert "LEFT OUTER JOIN post.post AS post_1" in compiled
    assert "post_1.published IS true" not in compiled


def test_service_parses_user_ids_and_preserves_input_order(
    monkeypatch,
) -> None:
    users = [
        Mock(id=8, posts=[]),
        Mock(id=7, posts=[]),
    ]
    get_users = Mock(return_value=users)
    monkeypatch.setattr(
        user_service.user_repo, "get_users_with_posts", get_users
    )

    result = user_service.get_users_with_posts(
        Mock(),
        "7, 8,7",
        current_user=Mock(id=7),
    )

    assert [user.user_id for user in result] == [7, 8]
    get_users.assert_called_once()
    assert get_users.call_args.args[1:] == ([7, 8], 7)
    assert get_users.call_args.kwargs["is_admin"] is False


def test_admin_service_includes_admin_role_for_post_visibility(
    monkeypatch,
) -> None:
    admin = Mock(id=3, role="admin")
    get_users = Mock(return_value=[Mock(id=7, posts=[])])
    monkeypatch.setattr(
        user_service.user_repo, "get_users_with_posts", get_users
    )

    user_service.get_users_with_posts(Mock(), "7", current_user=admin)

    assert get_users.call_args.kwargs["is_admin"] is True
