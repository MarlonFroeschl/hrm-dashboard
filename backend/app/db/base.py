from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect schema changes via autogenerate
from app.models.audit_log import AuditLog  # noqa: E402, F401
from app.models.document import Document  # noqa: E402, F401
from app.models.employee_profile import EmployeeProfile  # noqa: E402, F401
from app.models.knowledge_entry import KnowledgeEntry  # noqa: E402, F401
from app.models.offboarding_plan import OffboardingPlan  # noqa: E402, F401
from app.models.onboarding_task import OnboardingTask  # noqa: E402, F401
from app.models.person import Person  # noqa: E402, F401
