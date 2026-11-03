from sqlalchemy.orm import Session

from models.post_models import Post
from schemas.post_schemas import PostCreate


def get_all_posts(
    db: Session, page: int, limit: int
) -> dict[str, int | list[Post]]:
    query = db.query(Post).order_by(Post.id)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"page": page, "limit": limit, "total": total, "items": items}


def get_post_by_id(db: Session, post_id: int) -> Post | None:
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(db: Session, post_data: PostCreate) -> Post:
    post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=post_data.user_id,
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
