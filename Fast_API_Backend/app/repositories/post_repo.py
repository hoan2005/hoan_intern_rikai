from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.post_models import Post
from app.schemas.post_schemas import PostCreate


def get_all_posts(
    db: Session,
    page: int,
    limit: int,
    author_id: int | None = None,
    category: str | None = None,
    published: bool | None = None,
    search: str | None = None,
    current_user_id: int | None = None,
    is_admin: bool = False,
) -> dict[str, int | list[Post]]:
    query = db.query(Post)
    if not is_admin:
        if current_user_id is None:
            query = query.filter(Post.published.is_(True))
        else:
            query = query.filter(
                or_(
                    Post.published.is_(True),
                    Post.user_id == current_user_id,
                )
            )
    if search is not None:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern),
            )
        )
    if author_id is not None:
        query = query.filter(Post.user_id == author_id)
    if category is not None:
        query = query.filter(Post.category == category)
    if published is not None:
        query = query.filter(Post.published == published)
    total = query.count()
    query = query.order_by(Post.created_at, Post.id)
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"page": page, "limit": limit, "total": total, "items": items}


def get_post_by_id(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def get_user_posts(
    db: Session,
    user_id: int,
    include_unpublished: bool,
) -> list[Post]:
    query = db.query(Post).filter(Post.user_id == user_id)
    if not include_unpublished:
        query = query.filter(Post.published.is_(True))
    return query.order_by(Post.created_at, Post.id).all()


def create_post(db: Session, post_data: PostCreate, user_id: int) -> Post:
    post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=user_id,
        category=post_data.category,
        published=post_data.published,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post: Post, update_data: dict) -> Post:
    for field, value in update_data.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()
