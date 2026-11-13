from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NoteTag(Base):
    __tablename__ = "note_tags"
    __table_args__ = (
        PrimaryKeyConstraint("note_id", "tag_id", name="pk_note_tags"),
    )

    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE")
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE")
    )
