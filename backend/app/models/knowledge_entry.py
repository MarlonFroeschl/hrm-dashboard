import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.person import Person


class EntryType(str, enum.Enum):
    voice_note = "voice_note"
    interview = "interview"
    document = "document"
    protocol = "protocol"


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entry_type: Mapped[EntryType] = mapped_column(
        SAEnum(EntryType, name="entrytype", create_type=False),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    vector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=text("now()"),
        onupdate=func.now(),
    )

    # Relationships
    author: Mapped["Person"] = relationship(
        "Person",
        back_populates="knowledge_entries",
        foreign_keys=[author_id],
    )

    __table_args__ = (
        Index("idx_knowledge_entries_author_id", "author_id"),
        Index("idx_knowledge_entries_entry_type", "entry_type"),
        Index("idx_knowledge_entries_vector_id", "vector_id"),
        Index("idx_knowledge_entries_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<KnowledgeEntry id={self.id} type={self.entry_type}>"
