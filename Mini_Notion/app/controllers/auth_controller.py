from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import (
    EMAIL_ALREADY_REGISTERED,
    INVALID_CREDENTIALS,
    PASSWORD_CONFIRMATION_MISMATCH,
)
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    PasswordConfirmationMismatchError,
    login_user,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: DbSession) -> User:
    try:
        return register_user(db, payload)
    except PasswordConfirmationMismatchError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=PASSWORD_CONFIRMATION_MISMATCH,
        ) from error
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EMAIL_ALREADY_REGISTERED,
        ) from error


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    try:
        return login_user(db, payload.email, payload.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser) -> User:
    return current_user
