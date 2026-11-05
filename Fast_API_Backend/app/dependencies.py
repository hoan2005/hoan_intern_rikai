from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal
from app.models.user_models import User
from app.repositories import user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_user_from_token(token: str, db: Session) -> User:
    if not settings.JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT_SECRET_KEY chưa được cấu hình.",
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Thông tin xác thực không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
        subject = payload["sub"]
        if not isinstance(subject, str):
            raise credentials_exception
        user_id = int(subject)
        if user_id <= 0:
            raise credentials_exception
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if token is None:
        return None
    return _get_user_from_token(token, db)


def get_current_user(
    current_user: User | None = Depends(get_optional_current_user),
) -> User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    user = _get_user_from_token(token, db)
    return user.id


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa đủ quyền thực hiện thao tác này.",
        )
    return current_user
