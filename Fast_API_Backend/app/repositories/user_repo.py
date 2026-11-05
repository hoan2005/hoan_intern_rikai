from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.post_models import Post
from app.models.user_models import User


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username_or_email(
    db: Session, username_or_email: str
) -> User | None:
    return (
        db.query(User)
        .filter(
            or_(
                User.username == username_or_email,
                User.email == username_or_email,
            )
        )
        .first()
    )


def get_user_posts(user: User) -> list[Post]:
    return user.posts


def create_user(db: Session, user: User) -> User:
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user


def update_user(db: Session, user: User, update_data: dict) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> str:
    db.delete(user)
    db.commit()
    return "Người dùng đã được xóa thành công."
