import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.document import Document
    from app.models.employee_profile import EmployeeProfile
    from app.models.knowledge_entry import KnowledgeEntry


class PersonType(str, enum.Enum):
    applicant = "applicant"
    employee = "employee"
    alumni = "alumni"


class PersonStatus(str, enum.Enum):
    active = "active"
    onboarding = "onboarding"
    offboarding = "offboarding"
    archived = "archived"


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    person_type: Mapped[PersonType] = mapped_column(
        SAEnum(PersonType, name="persontype", create_type=False),
        nullable=False,
    )
    status: Mapped[PersonStatus] = mapped_column(
        SAEnum(PersonStatus, name="personstatus", create_type=False),
        nullable=False,
        default=PersonStatus.active,
        server_default="active",
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
    employee_profile: Mapped["EmployeeProfile | None"] = relationship(
        "EmployeeProfile",
        back_populates="person",
        uselist=False,
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="person",
        cascade="all, delete-orphan",
    )
    knowledge_entries: Mapped[list["KnowledgeEntry"]] = relationship(
        "KnowledgeEntry",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    audit_logs_performed: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="performer",
        foreign_keys="AuditLog.performed_by",
    )

    __table_args__ = (
        Index("idx_persons_person_type", "person_type"),
        Index("idx_persons_status", "status"),
        Index("idx_persons_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Person id={self.id} email={self.email} type={self.person_type}>"
