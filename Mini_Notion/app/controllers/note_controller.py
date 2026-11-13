from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import NOTE_NOT_FOUND
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.note_schema import NoteList, NoteRead, NoteUpdate
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["notes"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=NoteList)
def list_notes(
    db: DbSession,
    current_user: CurrentUser,
    collection_id: Annotated[int | None, Query(ge=1)] = None,
    query: Annotated[str | None, Query(alias="q", max_length=255)] = None,
    tag: Annotated[str | None, Query(max_length=50)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NoteList:
    items, total = note_service.list_notes(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        collection_id=collection_id,
        query=query,
        tag=tag,
    )
    return NoteList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{id}", response_model=NoteRead)
def get_note(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> NoteRead:
    note = note_service.get_note(db, id, current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOTE_NOT_FOUND,
        )
    return note


@router.patch("/{id}", response_model=NoteRead)
def update_note(
    id: int,
    payload: NoteUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> NoteRead:
    note = note_service.get_note(db, id, current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOTE_NOT_FOUND,
        )
    return note_service.update_note(db, note, payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    note = note_service.get_note(db, id, current_user.id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOTE_NOT_FOUND,
        )
    note_service.delete_note(db, note)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
