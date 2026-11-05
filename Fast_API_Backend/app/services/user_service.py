import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.post_models import Post
from app.models.user_models import User
from app.repositories import post_repo, user_repo
from app.schemas.user_schemas import UserCreate, UserUpdate


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=settings.SCRYPT_N,
        r=settings.SCRYPT_R,
        p=settings.SCRYPT_P,
    )
    return (
        f"{settings.SCRYPT_ALGORITHM}${settings.SCRYPT_N}"
        f"${settings.SCRYPT_R}${settings.SCRYPT_P}"
        f"${salt.hex()}${password_hash.hex()}"
    )


def get_all_users(db: Session) -> list[User]:
    return user_repo.get_all_users(db)


def get_user_by_id(db: Session, user_id: int) -> User:
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng với ID: {user_id}",
        )
    return user


def get_user_posts(
    db: Session,
    user_id: int,
    current_user_id: int | None = None,
    current_user_role: str | None = None,
) -> list[Post]:
    get_user_by_id(db, user_id)
    return post_repo.get_user_posts(
        db,
        user_id,
        include_unpublished=(
            current_user_role == "admin" or current_user_id == user_id
        ),
    )


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=_hash_password(user_data.password),
        role="user",
    )
    try:
        return user_repo.create_user(db, user)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tên người dùng hoặc email đã được sử dụng.",
        ) from exc


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp ít nhất một thông tin hợp lệ để cập nhật.",
        )
    if "password" in update_data:
        update_data["hashed_password"] = _hash_password(
            update_data.pop("password")
        )
    if "email" in update_data:
        update_data["email"] = str(update_data["email"])

    try:
        return user_repo.update_user(db, user, update_data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tên người dùng hoặc email đã được sử dụng.",
        ) from exc


def delete_user(db: Session, user_id: int) -> str:
    user = get_user_by_id(db, user_id)
    return user_repo.delete_user(db, user)
