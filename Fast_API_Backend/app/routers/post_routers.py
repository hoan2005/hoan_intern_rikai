from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import (
    get_current_user,
    get_db,
    get_optional_current_user,
)
from app.models.user_models import User
from app.schemas.post_schemas import (
    PaginatedPostResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["Quản lý bài viết"])


@router.get(
    "",
    response_model=PaginatedPostResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách bài viết",
)
def list_posts(
    page: int = Query(1, description="Số trang, bắt đầu từ 1"),
    limit: int = Query(10, description="Số bài viết mỗi trang, tối đa 100"),
    author_id: int | None = Query(None, description="Lọc theo ID tác giả"),
    category: str | None = Query(None, description="Lọc theo danh mục"),
    published: bool | None = Query(
        None, description="Lọc theo trạng thái xuất bản"
    ),
    search: str | None = Query(
        None, description="Tìm trong tiêu đề và nội dung"
    ),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    return post_service.get_all_posts(
        db,
        page,
        limit,
        author_id,
        category,
        published,
        search,
        current_user_id=current_user.id if current_user else None,
        current_user_role=current_user.role if current_user else None,
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết bài viết",
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return post_service.get_post_by_id(db, post_id, current_user)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo bài viết mới",
)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return post_service.create_post(db, post_data, current_user.id)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật bài viết",
)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return post_service.update_post(db, post_id, post_data, current_user)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa bài viết",
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post_service.delete_post(db, post_id, current_user)
