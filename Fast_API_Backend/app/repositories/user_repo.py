from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.post_models import Post
from app.models.user_models import User


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def get_users_with_posts(
    db: Session,
    user_ids: list[int],
    current_user_id: int | None,
    is_admin: bool = False,
) -> list[User]:
    if is_admin:
        visible_posts = True
    elif current_user_id is not None:
        visible_posts = or_(
            Post.published.is_(True),
            Post.user_id == current_user_id,
        )
    else:
        visible_posts = Post.published.is_(True)
    return (
        db.query(User)
        .options(joinedload(User.posts.and_(visible_posts)))
        .filter(User.id.in_(user_ids))
        .order_by(User.id)
        .all()
    )


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
        db.flush()
        db.add(
            Post(
                title="Chào mừng đến với Mini CRUD API",
                content=(
                    f"Xin chào {user.username}! Đây là bài viết đầu tiên "
                    "của bạn."
                ),
                user_id=user.id,
                category="Chào mừng",
            )
        )
        db.flush()
        db.refresh(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
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
