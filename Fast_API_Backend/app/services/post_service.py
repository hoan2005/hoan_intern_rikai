from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.post_models import Post
from app.repositories import post_repo, user_repo
from app.schemas.post_schemas import PostCreate, PostUpdate


def get_all_posts(
    db: Session,
    page: int = 1,
    limit: int = 10,
    author_id: int | None = None,
    category: str | None = None,
    published: bool | None = None,
    search: str | None = None,
    current_user_id: int | None = None,
    current_user_role: str | None = None,
) -> dict[str, int | list[Post]]:
    return post_repo.get_all_posts(
        db,
        page,
        limit,
        author_id,
        category,
        published,
        search,
        current_user_id=current_user_id,
        is_admin=current_user_role == "admin",
    )


def get_post_by_id(db: Session, post_id: int) -> Post:
    post = post_repo.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết với ID: {post_id}",
        )
    return post


def _ensure_user_exists(db: Session, user_id: int) -> None:
    if user_repo.get_user_by_id(db, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng với ID: {user_id}",
        )


def create_post(db: Session, post_data: PostCreate, user_id: int) -> Post:
    _ensure_user_exists(db, user_id)
    return post_repo.create_post(db, post_data, user_id)


def update_post(
    db: Session,
    post: Post,
    post_data: PostUpdate,
) -> Post:
    update_data = post_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp ít nhất một thông tin hợp lệ để cập nhật.",
        )
    return post_repo.update_post(db, post, update_data)


def delete_post(db: Session, post: Post) -> None:
    post_repo.delete_post(db, post)
