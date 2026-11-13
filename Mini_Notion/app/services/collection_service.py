from sqlalchemy.orm import Session

from app.models.collection_model import Collection
from app.repositories import collection_repository
from app.schemas.collection_schema import CollectionCreate, CollectionUpdate


def list_collections(
    db: Session, user_id: int, *, limit: int, offset: int
) -> tuple[list[Collection], int]:
    return collection_repository.list_collections(
        db, user_id, limit=limit, offset=offset
    )


def get_collection(
    db: Session, collection_id: int, user_id: int
) -> Collection | None:
    return collection_repository.get_collection(db, collection_id, user_id)


def create_collection(
    db: Session, user_id: int, payload: CollectionCreate
) -> Collection:
    return collection_repository.create_collection(
        db,
        user_id=user_id,
        name=payload.name,
        description=payload.description,
    )


def update_collection(
    db: Session,
    collection: Collection,
    payload: CollectionUpdate,
) -> Collection:
    return collection_repository.update_collection(
        db,
        collection,
        payload.model_dump(exclude_unset=True),
    )


def delete_collection(db: Session, collection: Collection) -> None:
    collection_repository.delete_collection(db, collection)
