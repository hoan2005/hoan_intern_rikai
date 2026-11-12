from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user_model import User
from app.repositories import user_repository
from app.schemas.auth_schema import TokenResponse, UserCreate


class EmailAlreadyRegisteredError(Exception):
    pass


class PasswordConfirmationMismatchError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, user_data: UserCreate) -> User:
    if user_data.password != user_data.confirm_password:
        raise PasswordConfirmationMismatchError

    if user_repository.get_user_by_email(db, user_data.email) is not None:
        raise EmailAlreadyRegisteredError

    try:
        return user_repository.create_user(
            db,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
    except IntegrityError as error:
        raise EmailAlreadyRegisteredError from error


def login_user(db: Session, email: str, password: str) -> TokenResponse:
    user = user_repository.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )
