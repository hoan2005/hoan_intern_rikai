from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.post_schemas import PostResponse
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Quản lý người dùng"])


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng",
)
def list_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết người dùng theo ID",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)


@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách bài viết của người dùng",
)
def list_user_posts(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_posts(db, user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo người dùng mới",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin người dùng",
)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa người dùng",
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)
