import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user_models import User
from app.repositories import user_repo
from app.schemas.user_schemas import (
    UserCreate,
    UserPostsResponse,
    UserUpdate,
)


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


def get_users_with_posts(
    db: Session,
    user_ids_parameter: str,
    current_user: User | None = None,
) -> list[UserPostsResponse]:
    try:
        user_ids = list(
            dict.fromkeys(
                int(value.strip()) for value in user_ids_parameter.split(",")
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Danh sách ID người dùng không hợp lệ.",
        ) from exc
    if not user_ids or any(value <= 0 for value in user_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="ID người dùng phải lớn hơn 0.",
        )

    users = user_repo.get_users_with_posts(
        db,
        user_ids,
        current_user.id if current_user else None,
        is_admin=current_user is not None and current_user.role == "admin",
    )
    found_ids = {user.id for user in users}
    missing_id = next(
        (user_id for user_id in user_ids if user_id not in found_ids), None
    )
    if missing_id is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng với ID: {missing_id}",
        )
    users_by_id = {user.id: user for user in users}
    return [
        UserPostsResponse(
            user_id=user.id,
            posts=user.posts,
        )
        for user in (users_by_id[user_id] for user_id in user_ids)
    ]


def create_user(
    db: Session, user_data: UserCreate, current_user: User
) -> User:
    _ensure_admin(current_user)
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


def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
    current_user: User,
) -> User:
    if current_user.role != "admin" and (
        "role" in user_data.model_fields_set or user_id != current_user.id
    ):
        _raise_forbidden()
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


def delete_user(db: Session, user_id: int, current_user: User) -> str:
    _ensure_admin(current_user)
    user = get_user_by_id(db, user_id)
    return user_repo.delete_user(db, user)


def _ensure_admin(current_user: User) -> None:
    if current_user.role != "admin":
        _raise_forbidden()


def _raise_forbidden() -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Bạn chưa đủ quyền thực hiện thao tác này.",
    )
