import pytest
from pydantic import ValidationError

from app.schemas.user_schemas import UserCreate, UserUpdate


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
