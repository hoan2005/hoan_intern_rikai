from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import COLLECTION_NOT_FOUND
from app.db.session import get_db
from app.models.collection_model import Collection
from app.models.user_model import User
from app.schemas.collection_schema import (
    CollectionCreate,
    CollectionList,
    CollectionRead,
    CollectionUpdate,
)
from app.schemas.note_schema import NoteCreate, NoteList, NoteRead
from app.services import collection_service
from app.services import note_service

router = APIRouter(prefix="/collections", tags=["collections"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=CollectionList)
def list_collections(
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CollectionList:
    items, total = collection_service.list_collections(
        db, current_user.id, limit=limit, offset=offset
    )
    return CollectionList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_collection(
    payload: CollectionCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Collection:
    return collection_service.create_collection(db, current_user.id, payload)


@router.get("/{id}", response_model=CollectionRead)
def get_collection(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Collection:
    collection = collection_service.get_collection(db, id, current_user.id)
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLLECTION_NOT_FOUND,
        )
    return collection


@router.patch("/{id}", response_model=CollectionRead)
def update_collection(
    id: int,
    payload: CollectionUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Collection:
    collection = collection_service.get_collection(db, id, current_user.id)
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLLECTION_NOT_FOUND,
        )
    return collection_service.update_collection(db, collection, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_collection(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    collection = collection_service.get_collection(db, id, current_user.id)
    if collection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLLECTION_NOT_FOUND,
        )
    collection_service.delete_collection(db, collection)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    id: int,
    payload: NoteCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> NoteRead:
    note = note_service.create_note(db, id, current_user.id, payload)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLLECTION_NOT_FOUND,
        )
    return note


@router.get("/{id}/notes", response_model=NoteList)
def list_collection_notes(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
    query: Annotated[str | None, Query(alias="q", max_length=255)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> NoteList:
    result = note_service.list_collection_notes(
        db,
        id,
        current_user.id,
        limit=limit,
        offset=offset,
        query=query,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLLECTION_NOT_FOUND,
        )
    items, total = result
    return NoteList(items=items, total=total, limit=limit, offset=offset)
