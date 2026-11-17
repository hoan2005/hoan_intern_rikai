from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tag_model import Tag


def list_tags(db: Session, user_id: int, *, limit: int, offset: int) -> tuple[list[Tag], int]:
    owner_filter = Tag.user_id == user_id
    items = list(
        db.scalars(
            select(Tag)
            .where(owner_filter)
            .order_by(Tag.id)
            .limit(limit)
            .offset(offset)
        )
    )
    total = db.scalar(
        select(func.count()).select_from(Tag).where(owner_filter)
    )
    return items, total or 0


def get_tag(db: Session, tag_id: int, user_id: int) -> Tag | None:
    return db.scalar(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == user_id,
        )
    )


def get_tag_by_name(db: Session, name: str, user_id: int) -> Tag | None:
    return db.scalar(
        select(Tag).where(
            Tag.user_id == user_id,
            Tag.name == name,
        )
    )


def create_tag(db: Session, *, user_id: int, name: str) -> Tag | None:
    tag = Tag(user_id=user_id, name=name)
    db.add(tag)
    try:
        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError:
        db.rollback()
        return None


def delete_tag(db: Session, tag: Tag) -> None:
    db.delete(tag)
    db.commit()