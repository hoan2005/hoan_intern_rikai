from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.errors import TAG_ALREADY_EXISTS, TAG_NOT_FOUND
from app.core.permissions import (
    RequireTagsCreate,
    RequireTagsDelete,
    RequireTagsRead,
)
from app.db.session import get_db
from app.models.user_model import User
from app.schemas.tag_schema import TagCreate, TagList, TagRead
from app.services import tag_service

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    dependencies=[Depends(get_current_user)],
)
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=TagList)
def list_tags(
    db: DbSession,
    current_user: CurrentUser,
    _: Annotated[User, Depends(RequireTagsRead)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TagList:
    items, total = tag_service.list_tags(
        db, current_user.id, limit=limit, offset=offset
    )
    return TagList(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    payload: TagCreate,
    db: DbSession,
    current_user: CurrentUser,
    _: Annotated[User, Depends(RequireTagsCreate)],
) -> TagRead:
    tag = tag_service.create_tag(db, current_user.id, payload)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=TAG_ALREADY_EXISTS,
        )
    return tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tag(
    tag_id: int,
    db: DbSession,
    current_user: CurrentUser,
    _: Annotated[User, Depends(RequireTagsDelete)],
) -> Response:
    tag = tag_service.get_tag(db, tag_id, current_user.id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TAG_NOT_FOUND,
        )
    tag_service.delete_tag(db, tag)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
