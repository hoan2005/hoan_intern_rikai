from sqlalchemy.orm import Session

from app.models.tag_model import Tag
from app.repositories import tag_repository
from app.schemas.tag_schema import TagCreate


def list_tags(
    db: Session, user_id: int, *, limit: int, offset: int
) -> tuple[list[Tag], int]:
    return tag_repository.list_tags(db, user_id, limit=limit, offset=offset)


def get_tag(db: Session, tag_id: int, user_id: int) -> Tag | None:
    return tag_repository.get_tag(db, tag_id, user_id)


def create_tag(db: Session, user_id: int, payload: TagCreate) -> Tag | None:
    return tag_repository.create_tag(db, user_id=user_id, name=payload.name)


def delete_tag(db: Session, tag: Tag) -> None:
    tag_repository.delete_tag(db, tag)