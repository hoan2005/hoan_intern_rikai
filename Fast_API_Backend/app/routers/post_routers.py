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
    description=(
        "Trả về danh sách bài viết có phân trang, sắp xếp theo thời gian tạo. "
        "Có thể lọc theo tác giả, danh mục và trạng thái xuất bản, hoặc tìm "
        "từ khóa trong tiêu đề/nội dung. Khách chỉ thấy bài đã xuất bản; "
        "người dùng thấy thêm bản nháp của mình, quản trị viên thấy tất cả."
    ),
    response_description="Trang bài viết và tổng số kết quả phù hợp.",
    responses={
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
        422: {
            "description": "Tham số lọc hoặc phân trang không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Số trang phải lớn hơn hoặc bằng 1."
                    }
                }
            },
        },
    },
)
def list_posts(
    page: int = Query(
        1, description="Số trang, bắt đầu từ 1; giá trị tối thiểu là 1"
    ),
    limit: int = Query(
        10, description="Số bài viết mỗi trang; giá trị từ 1 đến 100"
    ),
    author_id: int | None = Query(
        None, description="Lọc theo ID tác giả; nếu truyền phải lớn hơn 0"
    ),
    category: str | None = Query(
        None, description="Lọc theo danh mục; độ dài từ 1 đến 100 ký tự"
    ),
    published: bool | None = Query(
        None,
        description=(
            "Lọc theo trạng thái: true đã xuất bản, false bản nháp"
        ),
    ),
    search: str | None = Query(
        None, description="Tìm từ khóa không rỗng trong tiêu đề và nội dung"
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
    description=(
        "Lấy bài viết theo ID. Bài chưa xuất bản chỉ hiển thị với tác giả "
        "của bài hoặc quản trị viên; với các trường hợp khác API trả về 404."
    ),
    response_description="Thông tin bài viết.",
    responses={
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
            "description": (
                "Không tìm thấy bài viết hoặc bài viết không thể xem."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy bài viết với ID: 123"
                    }
                }
            },
        },
    },
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
    description=(
        "Tạo bài viết dưới tài khoản đang đăng nhập. `title` và `content` "
        "không được để trống; `published` mặc định là `false` nếu không gửi."
    ),
    response_description="Bài viết vừa được tạo.",
    responses={
        401: {
            "description": "Yêu cầu đăng nhập bằng access token.",
            "content": {
                "application/json": {
                    "example": {"detail": "Chưa đăng nhập."}
                }
            },
        },
        404: {
            "description": "Tài khoản hiện tại không còn tồn tại.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy người dùng với ID: 7"
                    }
                }
            },
        },
        422: {
            "description": "Dữ liệu bài viết không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "field": "title",
                                "message": "Tiêu đề không được để trống.",
                            }
                        ]
                    }
                }
            },
        },
    },
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
    description=(
        "Cập nhật một hoặc nhiều trường của bài viết. Chỉ tác giả của bài "
        "hoặc quản trị viên được phép; cần gửi ít nhất một trường cần đổi."
    ),
    response_description="Bài viết sau khi cập nhật.",
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
            "description": "Người gọi không phải tác giả hoặc quản trị viên.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Bạn chưa đủ quyền thực hiện thao tác này."
                    }
                }
            },
        },
        404: {
            "description": "Không tìm thấy bài viết với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy bài viết với ID: 123"
                    }
                }
            },
        },
        422: {
            "description": "Dữ liệu cập nhật không hợp lệ.",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "field": "title",
                                "message": "Tiêu đề không được để trống.",
                            }
                        ]
                    }
                }
            },
        },
    },
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
    description=(
        "Xóa bài viết theo ID. Chỉ tác giả của bài hoặc quản trị viên được "
        "phép. Thành công trả về `204 No Content` và không có nội dung "
        "phản hồi."
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
            "description": "Người gọi không phải tác giả hoặc quản trị viên.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Bạn chưa đủ quyền thực hiện thao tác này."
                    }
                }
            },
        },
        404: {
            "description": "Không tìm thấy bài viết với ID đã cung cấp.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Không tìm thấy bài viết với ID: 123"
                    }
                }
            },
        },
    },
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post_service.delete_post(db, post_id, current_user)
