from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import (
    get_current_user,
    get_db,
    get_optional_current_user,
)
from app.models.user_models import User
from app.schemas.post_schemas import PostResponse
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Quản lý người dùng"])


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng",
    description=(
        "Lấy danh sách tài khoản. Yêu cầu đăng nhập; chỉ trả về thông tin "
        "công khai, không bao gồm mật khẩu."
    ),
    response_description="Danh sách người dùng.",
    responses={
        200: {
            "description": "Danh sách người dùng.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 7,
                            "username": "nguyenvana",
                            "email": "vana123@gmail.com",
                            "role": "user",
                        }
                    ]
                }
            },
        },
        401: {
            "description": "Yêu cầu đăng nhập bằng access token.",
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
    },
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return user_service.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết người dùng theo ID",
    description=(
        "Lấy thông tin công khai của một người dùng. Yêu cầu access token; "
        "`user_id` là ID tài khoản cần tra cứu."
    ),
    response_description="Thông tin công khai của người dùng.",
    responses={
        401: {
            "description": (
                "Thiếu access token hoặc token không hợp lệ/hết hạn."
            ),
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
        404: {
            "description": "Không tìm thấy người dùng với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy người dùng với ID: 123"
                    }
                }
            },
        },
    },
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return user_service.get_user_by_id(db, user_id)


@router.get(
    "/{user_id}/posts",
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách bài viết của người dùng",
    description=(
        "Lấy các bài viết public của tác giả có ID tương ứng. Khách chưa đăng nhập "
        "chỉ thấy bài đã xuất bản; tác giả đăng nhập và quản trị viên có thể "
        "thấy cả bài chưa xuất bản theo quyền truy cập."
    ),
    response_description="Danh sách bài viết mà người gọi được phép xem.",
    responses={
        200: {
            "description": "Danh sách bài viết mà người gọi được phép xem.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Bắt đầu với FastAPI",
                            "content": (
                                "FastAPI giúp xây dựng API Python nhanh chóng."
                            ),
                            "user_id": 7,
                            "category": "Công nghệ",
                            "published": True,
                            "created_at": "2026-01-01T10:00:00Z",
                        }
                    ]
                }
            },
        },
        401: {
            "description": "Token đã cung cấp không hợp lệ hoặc hết hạn.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Thông tin xác thực không hợp lệ hoặc đã hết hạn."
                        )
                    }
                }
            },
        },
        404: {
            "description": "Không tìm thấy người dùng với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy người dùng với ID: 123"
                    }
                }
            },
        },
    },
)
def list_user_posts(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return user_service.get_user_posts(
        db,
        user_id,
        current_user.id if current_user else None,
        current_user.role if current_user else None,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo người dùng mới",
    description=(
        "Tạo tài khoản mới. Chỉ quản trị viên được phép gọi API này; vai trò "
        "mới luôn là `user` và mật khẩu không xuất hiện trong phản hồi."
    ),
    response_description="Tài khoản vừa được tạo.",
    responses={
        401: {
            "description": (
                "Thiếu access token hoặc token không hợp lệ/hết hạn."
            ),
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
        403: {
            "description": "Người gọi không có quyền quản trị viên.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Bạn chưa đủ quyền thực hiện thao tác này."
                    }
                }
            },
        },
        409: {
            "description": "Tên người dùng hoặc email đã được sử dụng.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Tên người dùng hoặc email đã được sử dụng."
                        )
                    }
                }
            },
        },
        422: {
            "description": "Dữ liệu đầu vào không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "field": "username",
                                "message": (
                                    "Tên người dùng phải có ít nhất 3 ký tự."
                                ),
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.create_user(db, user_data, current_user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin người dùng",
    description=(
        "Cập nhật một hoặc nhiều trường bằng cách gửi riêng các trường "
        "cần thay đổi. Người dùng chỉ được cập nhật hồ sơ của mình; thay đổi "
        "vai trò yêu cầu quyền quản trị viên."
    ),
    response_description="Thông tin người dùng sau khi cập nhật.",
    responses={
        400: {
            "description": "Không có trường hợp lệ để cập nhật.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Cần cung cấp ít nhất một thông tin hợp lệ để "
                            "cập nhật."
                        )
                    }
                }
            },
        },
        401: {
            "description": (
                "Thiếu access token hoặc token không hợp lệ/hết hạn."
            ),
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
        403: {
            "description": "Không có quyền cập nhật tài khoản này.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Bạn chưa đủ quyền thực hiện thao tác này."
                    }
                }
            },
        },
        404: {
            "description": "Không tìm thấy người dùng với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy người dùng với ID: 123"
                    }
                }
            },
        },
        409: {
            "description": "Tên người dùng hoặc email đã được sử dụng.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Tên người dùng hoặc email đã được sử dụng."
                        )
                    }
                }
            },
        },
        422: {
            "description": "Dữ liệu đầu vào không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "field": "email",
                                "message": (
                                    "Email phải có dạng gồm chữ và số "
                                    "@gmail.com, chỉ dùng chữ cái và chữ số "
                                    "trước @."
                                ),
                            }
                        ]
                    }
                }
            },
        },
    },
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.update_user(db, user_id, user_data, current_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa người dùng",
    description=(
        "Xóa tài khoản theo ID. Chỉ quản trị viên được phép thực hiện. "
        "Thành công trả về `204 No Content` và không có nội dung phản hồi."
    ),
    response_description="Xóa thành công; phản hồi không có nội dung.",
    responses={
        401: {
            "description": (
                "Thiếu access token hoặc token không hợp lệ/hết hạn."
            ),
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
        403: {
            "description": "Người gọi không có quyền quản trị viên.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Bạn chưa đủ quyền thực hiện thao tác này."
                    }
                }
            },
        },
        404: {
            "description": "Không tìm thấy người dùng với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy người dùng với ID: 123"
                    }
                }
            },
        },
    },
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.delete_user(db, user_id, current_user)
