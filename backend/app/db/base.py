from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Models are imported lazily to avoid circular imports.
# Import them explicitly where needed, e.g.: from app.models import Person, Document
__all__ = [
    "AuditLog",
    "Document",
    "EmployeeProfile",
    "KnowledgeEntry",
    "OffboardingPlan",
    "OnboardingTask",
    "Person",
]
