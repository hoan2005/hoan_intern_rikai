from controller import user as user_controller
from fastapi import APIRouter, status
from Schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Quản lý người dùng"])


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng",
)
def list_users():
  """Lấy danh sách tất cả người dùng (Không hiển thị mật khẩu)."""
  return user_controller.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết người dùng theo ID",
)
def get_user(user_id: int):
  """Xem thông tin chi tiết của một người dùng theo ID (Không hiển thị mật khẩu)."""
  return user_controller.get_user_by_id(user_id)


@router.post(
    "/them",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo người dùng mới",
)
def create_user(user: UserCreate):
  """Tạo mới một người dùng (Có nhận mật khẩu vào nhưng trả về sẽ ẩn mật khẩu)."""

  return user_controller.create_user(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin người dùng",
)
def update_user(user_id: int, user: UserUpdate):
  """Cập nhật thông tin người dùng theo ID."""
  return user_controller.update_user(user_id, user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa người dùng",
)
def delete_user(user_id: int):
  """Xóa người dùng khỏi hệ thống theo ID."""
  return user_controller.delete_user(user_id)