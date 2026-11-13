from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.collection_model import Collection


def list_collections(
    db: Session, user_id: int, *, limit: int, offset: int
) -> tuple[list[Collection], int]:
    owner_filter = Collection.user_id == user_id
    items = list(
        db.scalars(
            select(Collection)
            .where(owner_filter)
            .order_by(Collection.id)
            .limit(limit)
            .offset(offset)
        )
    )
    total = db.scalar(
        select(func.count()).select_from(Collection).where(owner_filter)
    )
    return items, total or 0


def get_collection(
    db: Session, collection_id: int, user_id: int
) -> Collection | None:
    return db.scalar(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user_id,
        )
    )


def create_collection(
    db: Session,
    *,
    user_id: int,
    name: str,
    description: str | None,
) -> Collection:
    collection = Collection(
        user_id=user_id,
        name=name,
        description=description,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def update_collection(
    db: Session, collection: Collection, changes: dict[str, object]
) -> Collection:
    for field, value in changes.items():
        setattr(collection, field, value)
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection: Collection) -> None:
    db.delete(collection)
    db.commit()
