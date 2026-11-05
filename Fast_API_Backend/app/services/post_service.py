from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.post_models import Post
from app.models.user_models import User
from app.repositories import post_repo, user_repo
from app.schemas.post_schemas import PostCreate, PostUpdate


def _validate_post_filters(
    page: int,
    limit: int,
    author_id: int | None,
    category: str | None,
    search: str | None,
) -> None:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Số trang phải lớn hơn hoặc bằng 1.",
        )
    if not 1 <= limit <= 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Số bài viết mỗi trang phải từ 1 đến 100.",
        )
    if author_id is not None and author_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="ID tác giả phải lớn hơn 0.",
        )
    if category is not None and not 1 <= len(category) <= 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Danh mục phải có từ 1 đến 100 ký tự.",
        )
    if search is not None and len(search) < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Từ khóa tìm kiếm không được để trống.",
        )


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
    _validate_post_filters(page, limit, author_id, category, search)
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


def get_post_by_id(
    db: Session, post_id: int, current_user: User | None
) -> Post:
    post = post_repo.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết với ID: {post_id}",
        )
    if not post.published and (
        current_user is None
        or (current_user.role != "admin" and post.user_id != current_user.id)
    ):
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
    post_id: int,
    post_data: PostUpdate,
    current_user: User,
) -> Post:
    post = post_repo.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết với ID: {post_id}",
        )
    _ensure_post_owner_or_admin(post, current_user)
    update_data = post_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp ít nhất một thông tin hợp lệ để cập nhật.",
        )
    return post_repo.update_post(db, post, update_data)


def delete_post(db: Session, post_id: int, current_user: User) -> None:
    post = post_repo.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết với ID: {post_id}",
        )
    _ensure_post_owner_or_admin(post, current_user)
    post_repo.delete_post(db, post)


def _ensure_post_owner_or_admin(post: Post, current_user: User) -> None:
    if current_user.role != "admin" and post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa đủ quyền thực hiện thao tác này.",
        )
