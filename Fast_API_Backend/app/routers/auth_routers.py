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
)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
