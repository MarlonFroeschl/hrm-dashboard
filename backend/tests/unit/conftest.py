"""Shared fixtures for unit tests.

All fixtures in this module operate without a live database connection.
SQLAlchemy table metadata is introspected directly on the model classes.
"""

import pytest

from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.employee_profile import EmployeeProfile
from app.models.knowledge_entry import KnowledgeEntry
from app.models.offboarding_plan import OffboardingPlan
from app.models.onboarding_task import OnboardingTask
from app.models.person import Person


@pytest.fixture(scope="session")
def person_table():
    return Person.__table__


@pytest.fixture(scope="session")
def employee_profile_table():
    return EmployeeProfile.__table__


@pytest.fixture(scope="session")
def document_table():
    return Document.__table__


@pytest.fixture(scope="session")
def knowledge_entry_table():
    return KnowledgeEntry.__table__


@pytest.fixture(scope="session")
def onboarding_task_table():
    return OnboardingTask.__table__


@pytest.fixture(scope="session")
def offboarding_plan_table():
    return OffboardingPlan.__table__


@pytest.fixture(scope="session")
def audit_log_table():
    return AuditLog.__table__
