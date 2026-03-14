import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee_profile import EmployeeProfile


class InterviewSlot(TypedDict):
    week: int
    date: str
    topics: list[str]
    done: bool


class OffboardingPlan(Base):
    __tablename__ = "offboarding_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    trigger_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_day: Mapped[date] = mapped_column(Date, nullable=False)
    knowledge_extraction_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    weekly_interview_schedule: Mapped[list[InterviewSlot]] = mapped_column(
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
    employee: Mapped["EmployeeProfile"] = relationship(
        "EmployeeProfile",
        back_populates="offboarding_plans",
    )

    __table_args__ = (
        Index("idx_offboarding_plans_employee_id", "employee_id"),
        Index("idx_offboarding_plans_last_day", "last_day"),
        Index("idx_offboarding_plans_trigger_date", "trigger_date"),
    )

    def __repr__(self) -> str:
        return f"<OffboardingPlan id={self.id} employee_id={self.employee_id} last_day={self.last_day}>"
