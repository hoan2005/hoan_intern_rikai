from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user_models import User
from app.schemas.user_schemas import TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(tags=["Xác thực"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập và nhận access token",
    description=(
        "Xác thực bằng tên người dùng hoặc email cùng mật khẩu. Gửi dữ liệu "
        "dạng `application/x-www-form-urlencoded`; dùng access token trả về "
        "trong header `Authorization: Bearer <token>` cho các API cần "
        "đăng nhập."
    ),
    response_description=(
        "Access token dùng để xác thực các yêu cầu tiếp theo."
    ),
    responses={
        401: {
            "description": (
                "Tên đăng nhập/email hoặc mật khẩu không "
                "chính xác."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Tên đăng nhập/email hoặc mật khẩu "
                            "không chính xác."
                        )
                    }
                }
            },
        },
        422: {
            "description": "Thiếu hoặc sai định dạng trường biểu mẫu.",
            "content": {
                "application/json": {
                    "example": {
                        "errors": [
                            {
                                "field": "username",
                                "message": "Field required",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Máy chủ chưa cấu hình khóa ký JWT.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "JWT_SECRET_KEY chưa được cấu hình."
                    }
                }
            },
        },
    },
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Tên người dùng hoặc email.",
                            },
                            "password": {
                                "type": "string",
                                "format": "password",
                                "description": "Mật khẩu tài khoản.",
                            },
                        },
                        "required": ["username", "password"],
                    },
                    "example": {
                        "username": "nguyenvana",
                        "password": "secret123",
                    },
                }
            },
        }
    },
)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user_id = auth_service.authenticate_user(
        db, credentials.username, credentials.password
    )
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập/email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(
        access_token=auth_service.create_access_token(user_id)
    )


@router.get(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy hồ sơ người dùng đang đăng nhập",
    description=(
        "Trả về thông tin tài khoản tương ứng với access token trong header "
        "`Authorization: Bearer <token>`. Mật khẩu không được trả về."
    ),
    response_description="Thông tin công khai của người dùng hiện tại.",
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
    },
)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
