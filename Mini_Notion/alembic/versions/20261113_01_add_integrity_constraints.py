"""Add model integrity constraints to existing tables.

Revision ID: 20261113_01
Revises:
Create Date: 2026-11-13
"""

from alembic import context, op
import sqlalchemy as sa

revision = "20261113_01"
down_revision = None
branch_labels = None
depends_on = None


def _has_unique(table_name: str, columns: tuple[str, ...]) -> bool:
    if context.is_offline_mode():
        return False

    inspector = sa.inspect(op.get_bind())
    target_columns = set(columns)
    if any(
        set(constraint.get("column_names") or []) == target_columns
        for constraint in inspector.get_unique_constraints(table_name)
    ):
        return True
    return any(
        index.get("unique")
        and set(index.get("column_names") or []) == target_columns
        for index in inspector.get_indexes(table_name)
    )


def _has_notes_index() -> bool:
    if context.is_offline_mode():
        return False

    inspector = sa.inspect(op.get_bind())
    for index in inspector.get_indexes("notes"):
        columns = index.get("column_names") or []
        if index.get("name") == "ix_notes_collection_updated_at_desc":
            return True
        if columns != ["collection_id", "updated_at"]:
            continue
        sorting = index.get("column_sorting") or {}
        updated_at_sort = sorting.get("updated_at", ())
        if "desc" in updated_at_sort:
            return True
    return False


def _has_note_tag_primary_key() -> bool:
    if context.is_offline_mode():
        return False

    inspector = sa.inspect(op.get_bind())
    primary_key = inspector.get_pk_constraint("note_tags")
    columns = primary_key.get("constrained_columns") or []
    if columns and columns != ["note_id", "tag_id"]:
        raise RuntimeError(
            "Khóa chính note_tags hiện có không khớp "
            "(note_id, tag_id); cần xử lý thủ công trước khi migrate."
        )
    return columns == ["note_id", "tag_id"]


def upgrade() -> None:
    if not _has_unique("users", ("email",)):
        op.create_unique_constraint("uq_users_email", "users", ["email"])

    if not _has_unique("tags", ("user_id", "name")):
        op.create_unique_constraint(
            "uq_tags_user_id_name", "tags", ["user_id", "name"]
        )

    if not _has_notes_index():
        op.create_index(
            "ix_notes_collection_updated_at_desc",
            "notes",
            ["collection_id", sa.text("updated_at DESC")],
        )

    if not _has_note_tag_primary_key():
        op.create_primary_key(
            "pk_note_tags", "note_tags", ["note_id", "tag_id"]
        )


def downgrade() -> None:
    if context.is_offline_mode():
        op.drop_constraint("pk_note_tags", "note_tags", type_="primary")
        op.drop_index(
            "ix_notes_collection_updated_at_desc", table_name="notes"
        )
        op.drop_constraint("uq_tags_user_id_name", "tags", type_="unique")
        op.drop_constraint("uq_users_email", "users", type_="unique")
        return

    inspector = sa.inspect(op.get_bind())
    if any(
        item.get("name") == "pk_note_tags"
        for item in [inspector.get_pk_constraint("note_tags")]
    ):
        op.drop_constraint("pk_note_tags", "note_tags", type_="primary")
    if any(
        index.get("name") == "ix_notes_collection_updated_at_desc"
        for index in inspector.get_indexes("notes")
    ):
        op.drop_index(
            "ix_notes_collection_updated_at_desc", table_name="notes"
        )
    if any(
        constraint.get("name") == "uq_tags_user_id_name"
        for constraint in inspector.get_unique_constraints("tags")
    ):
        op.drop_constraint("uq_tags_user_id_name", "tags", type_="unique")
    if any(
        constraint.get("name") == "uq_users_email"
        for constraint in inspector.get_unique_constraints("users")
    ):
        op.drop_constraint("uq_users_email", "users", type_="unique")
