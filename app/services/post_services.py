from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories import post_repository, user_repository
from schemas.post_schemas import PostCreate, PostUpdate
from models.post_models import Post


def get_all_posts(
    db: Session, page: int = 1, limit: int = 10
) -> dict[str, int | list[Post]]:
    return post_repository.get_all_posts(db, page, limit)


def get_post_by_id(db: Session, post_id: int) -> Post:
    post = post_repository.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết với ID: {post_id}",
        )
    return post


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if user_repository.get_user_by_id(db, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng với ID: {user_id}",
        )


def create_post(db: Session, post_data: PostCreate) -> Post:
    _ensure_user_exists(db, post_data.user_id)
    return post_repository.create_post(db, post_data)


def update_post(db: Session, post_id: int, post_data: PostUpdate) -> Post:
    post = get_post_by_id(db, post_id)
    update_data = post_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp ít nhất một thông tin hợp lệ để cập nhật.",
        )
    if "user_id" in update_data:
        _ensure_user_exists(db, update_data["user_id"])
    return post_repository.update_post(db, post, update_data)


def delete_post(db: Session, post_id: int) -> None:
    post = get_post_by_id(db, post_id)
    post_repository.delete_post(db, post)
