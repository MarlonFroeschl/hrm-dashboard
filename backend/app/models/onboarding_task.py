import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.employee_profile import EmployeeProfile


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

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
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="taskstatus", create_type=False),
        nullable=False,
        default=TaskStatus.pending,
        server_default="pending",
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        server_default=text("now()"),
    )

    # Relationships
    employee: Mapped["EmployeeProfile"] = relationship(
        "EmployeeProfile",
        back_populates="onboarding_tasks",
    )

    __table_args__ = (
        Index("idx_onboarding_tasks_employee_id", "employee_id"),
        Index("idx_onboarding_tasks_status", "status"),
        Index("idx_onboarding_tasks_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<OnboardingTask id={self.id} type={self.task_type} status={self.status}>"
