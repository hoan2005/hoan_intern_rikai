import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import user_repo
from app.schemas.user_schemas import TokenResponse


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, hash_hex = stored_hash.split("$")
        if (
            algorithm,
            n,
            r,
            p,
        ) != (
            settings.SCRYPT_ALGORITHM,
            str(settings.SCRYPT_N),
            str(settings.SCRYPT_R),
            str(settings.SCRYPT_P),
        ):
            return False
        expected_hash = bytes.fromhex(hash_hex)
        if len(expected_hash) != 64:
            return False
        actual_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=settings.SCRYPT_N,
            r=settings.SCRYPT_R,
            p=settings.SCRYPT_P,
            dklen=64,
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual_hash, expected_hash)


def authenticate_user(
    db: Session, username_or_email: str, password: str
) -> int | None:
    user = user_repo.get_user_by_username_or_email(db, username_or_email)
    if user is None or not _verify_password(password, user.hashed_password):
        return None
    return user.id


def login(db: Session, username_or_email: str, password: str) -> TokenResponse:
    user_id = authenticate_user(db, username_or_email, password)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập/email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user_id))


def create_access_token(user_id: int) -> str:
    if not settings.JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT_SECRET_KEY chưa được cấu hình.",
        )
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
