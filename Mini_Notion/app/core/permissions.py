"""Permission definitions and role-permission mapping.

Roles are simple string identifiers (e.g. "user", "admin").
Each permission is a string like "collections:create" or "tags:delete".
The `ROLE_PERMISSIONS` mapping defines which permissions each role has.
"""

from enum import Enum
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.dependencies import get_current_user
from app.models.user_model import User


class Permission(str, Enum):
    """Permission identifiers used across the API."""

    # Collections
    COLLECTIONS_READ = "collections:read"
    COLLECTIONS_CREATE = "collections:create"
    COLLECTIONS_UPDATE = "collections:update"
    COLLECTIONS_DELETE = "collections:delete"

    # Notes
    NOTES_READ = "notes:read"
    NOTES_CREATE = "notes:create"
    NOTES_UPDATE = "notes:update"
    NOTES_DELETE = "notes:delete"
    NOTES_MANAGE_TAGS = "notes:manage_tags"

    # Tags
    TAGS_READ = "tags:read"
    TAGS_CREATE = "tags:create"
    TAGS_DELETE = "tags:delete"


# Mapping role -> list of Permission values
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "user": {
        Permission.COLLECTIONS_READ,
        Permission.COLLECTIONS_CREATE,
        Permission.COLLECTIONS_UPDATE,
        Permission.COLLECTIONS_DELETE,
        Permission.NOTES_READ,
        Permission.NOTES_CREATE,
        Permission.NOTES_UPDATE,
        Permission.NOTES_DELETE,
        Permission.NOTES_MANAGE_TAGS,
        Permission.TAGS_READ,
        Permission.TAGS_CREATE,
        Permission.TAGS_DELETE,
    },
    "admin": {
        # Admin has every permission
        Permission.COLLECTIONS_READ,
        Permission.COLLECTIONS_CREATE,
        Permission.COLLECTIONS_UPDATE,
        Permission.COLLECTIONS_DELETE,
        Permission.NOTES_READ,
        Permission.NOTES_CREATE,
        Permission.NOTES_UPDATE,
        Permission.NOTES_DELETE,
        Permission.NOTES_MANAGE_TAGS,
        Permission.TAGS_READ,
        Permission.TAGS_CREATE,
        Permission.TAGS_DELETE,
    },
}


def get_user_permissions(user: User) -> set[Permission]:
    """Return the set of permissions for a given user based on their role."""
    return ROLE_PERMISSIONS.get(user.role, set())


def has_permission(user: User, permission: Permission) -> bool:
    """Check whether the user has the given permission."""
    return permission in get_user_permissions(user)


def require_role(required_role: str) -> Callable[..., User]:
    """Dependency factory that requires a user to have a specific role."""

    def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Quyền không đủ để thực hiện thao tác",
            )
        return current_user

    return role_dependency


def require_permission(permission: Permission) -> Callable[..., User]:
    """Dependency factory that requires a user to have a specific permission."""

    def permission_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Quyền không đủ để thực hiện thao tác",
            )
        return current_user

    return permission_dependency


# Pre-built dependencies for convenience
RequireUser = require_role("user")
RequireAdmin = require_role("admin")

RequireCollectionsRead = require_permission(Permission.COLLECTIONS_READ)
RequireCollectionsCreate = require_permission(Permission.COLLECTIONS_CREATE)
RequireCollectionsUpdate = require_permission(Permission.COLLECTIONS_UPDATE)
RequireCollectionsDelete = require_permission(Permission.COLLECTIONS_DELETE)

RequireNotesRead = require_permission(Permission.NOTES_READ)
RequireNotesCreate = require_permission(Permission.NOTES_CREATE)
RequireNotesUpdate = require_permission(Permission.NOTES_UPDATE)
RequireNotesDelete = require_permission(Permission.NOTES_DELETE)
RequireNotesManageTags = require_permission(Permission.NOTES_MANAGE_TAGS)

RequireTagsRead = require_permission(Permission.TAGS_READ)
RequireTagsCreate = require_permission(Permission.TAGS_CREATE)
RequireTagsDelete = require_permission(Permission.TAGS_DELETE)


# Re-export HTTPBearer for convenience
__all__ = [
    "Permission",
    "ROLE_PERMISSIONS",
    "get_user_permissions",
    "has_permission",
    "require_role",
    "require_permission",
    "RequireUser",
    "RequireAdmin",
    "RequireCollectionsRead",
    "RequireCollectionsCreate",
    "RequireCollectionsUpdate",
    "RequireCollectionsDelete",
    "RequireNotesRead",
    "RequireNotesCreate",
    "RequireNotesUpdate",
    "RequireNotesDelete",
    "RequireNotesManageTags",
    "RequireTagsRead",
    "RequireTagsCreate",
    "RequireTagsDelete",
]