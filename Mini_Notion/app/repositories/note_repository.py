from sqlalchemy import desc, exists, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.collection_model import Collection
from app.models.note_model import Note
from app.models.note_tag_model import NoteTag
from app.models.tag_model import Tag


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
    filters = [Collection.user_id == user_id]
    if collection_id is not None:
        filters.append(Note.collection_id == collection_id)
    if query:
        filters.append(Note.title.ilike(f"%{query}%"))
    if tag:
        filters.append(
            exists(
                select(NoteTag.note_id)
                .join(Tag, Tag.id == NoteTag.tag_id)
                .where(
                    NoteTag.note_id == Note.id,
                    Tag.user_id == user_id,
                    Tag.name == tag,
                )
            )
        )

    statement = (
        select(Note)
        .join(Collection, Collection.id == Note.collection_id)
        .where(*filters)
    )
    total = db.scalar(
        select(func.count())
        .select_from(Note)
        .join(Collection, Collection.id == Note.collection_id)
        .where(*filters)
    )
    items = list(
        db.scalars(
            statement.options(selectinload(Note.tags))
            .order_by(
                desc(Note.is_pinned),
                desc(Note.updated_at),
                desc(Note.id),
            )
            .limit(limit)
            .offset(offset)
        )
    )
    return items, total or 0


def get_owned_collection(
    db: Session, collection_id: int, user_id: int
) -> Collection | None:
    return db.scalar(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == user_id,
        )
    )


def get_note(db: Session, note_id: int, user_id: int) -> Note | None:
    return db.scalar(
        select(Note)
        .join(Collection, Collection.id == Note.collection_id)
        .where(
            Note.id == note_id,
            Collection.user_id == user_id,
        )
        .options(selectinload(Note.tags))
    )


def create_note(
    db: Session,
    *,
    collection_id: int,
    title: str,
    body: str | None,
) -> Note:
    note = Note(collection_id=collection_id, title=title, body=body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note: Note, changes: dict[str, object]) -> Note:
    for field, value in changes.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note) -> None:
    db.delete(note)
    db.commit()
