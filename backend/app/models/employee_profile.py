import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.offboarding_plan import OffboardingPlan
    from app.models.onboarding_task import OnboardingTask
    from app.models.person import Person


class ITAccessLevel(str, enum.Enum):
    none = "none"
    basic = "basic"
    standard = "standard"
    admin = "admin"


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    knowledge_areas: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )
    it_access_level: Mapped[ITAccessLevel] = mapped_column(
        SAEnum(ITAccessLevel, name="itaccesslevel", create_type=False),
        nullable=False,
        default=ITAccessLevel.none,
        server_default="none",
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
    person: Mapped["Person"] = relationship(
        "Person",
        back_populates="employee_profile",
    )
    manager: Mapped["EmployeeProfile | None"] = relationship(
        "EmployeeProfile",
        back_populates="direct_reports",
        remote_side="EmployeeProfile.id",
        foreign_keys=[manager_id],
    )
    direct_reports: Mapped[list["EmployeeProfile"]] = relationship(
        "EmployeeProfile",
        back_populates="manager",
        foreign_keys=[manager_id],
    )
    onboarding_tasks: Mapped[list["OnboardingTask"]] = relationship(
        "OnboardingTask",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    offboarding_plans: Mapped[list["OffboardingPlan"]] = relationship(
        "OffboardingPlan",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_employee_profiles_department", "department"),
        Index("idx_employee_profiles_manager_id", "manager_id"),
        Index("idx_employee_profiles_start_date", "start_date"),
    )

    def __repr__(self) -> str:
        return f"<EmployeeProfile id={self.id} role={self.role} department={self.department}>"
