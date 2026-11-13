from sqlalchemy.orm import Session

from app.models.note_model import Note
from app.repositories import note_repository
from app.schemas.note_schema import NoteCreate, NoteUpdate


def list_collection_notes(
    db: Session,
    collection_id: int,
    user_id: int,
    *,
    limit: int,
    offset: int,
    query: str | None,
) -> tuple[list[Note], int] | None:
    collection = note_repository.get_owned_collection(
        db, collection_id, user_id
    )
    if collection is None:
        return None
    return list_notes(
        db,
        user_id,
        limit=limit,
        offset=offset,
        collection_id=collection_id,
        query=query,
        tag=None,
    )


def list_notes(
    db: Session,
    user_id: int,
    *,
    limit: int,
    offset: int,
    collection_id: int | None,
    query: str | None,
    tag: str | None,
) -> tuple[list[Note], int]:
    return note_repository.list_notes(
        db,
        user_id,
        limit=limit,
        offset=offset,
        collection_id=collection_id,
        query=query.strip() if query else None,
        tag=tag.strip() if tag else None,
    )


def get_note(db: Session, note_id: int, user_id: int) -> Note | None:
    return note_repository.get_note(db, note_id, user_id)


def create_note(
    db: Session,
    collection_id: int,
    user_id: int,
    payload: NoteCreate,
) -> Note | None:
    collection = note_repository.get_owned_collection(
        db, collection_id, user_id
    )
    if collection is None:
        return None
    return note_repository.create_note(
        db,
        collection_id=collection_id,
        title=payload.title,
        body=payload.body,
    )


def update_note(db: Session, note: Note, payload: NoteUpdate) -> Note:
    return note_repository.update_note(
        db, note, payload.model_dump(exclude_unset=True)
    )


def delete_note(db: Session, note: Note) -> None:
    note_repository.delete_note(db, note)
