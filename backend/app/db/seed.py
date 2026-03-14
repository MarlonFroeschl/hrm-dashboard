"""Seed script for development data.

Run from the backend/ directory:
    python -m app.db.seed

Idempotent: skips seeding if data already exists.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.audit_log import AuditAction, AuditLog
from app.models.document import Document
from app.models.employee_profile import EmployeeProfile, ITAccessLevel
from app.models.knowledge_entry import EntryType, KnowledgeEntry
from app.models.offboarding_plan import OffboardingPlan
from app.models.onboarding_task import OnboardingTask, TaskStatus
from app.models.person import Person, PersonStatus, PersonType


def seed_database(db: Session) -> None:
    # Skip if data already exists
    if db.query(Person).count() > 0:
        print("Seed data already present – skipping.")
        return

    print("Seeding development data...")

    # ── Persons ───────────────────────────────────────────────────────────────
    applicant = Person(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        first_name="Anna",
        last_name="Müller",
        email="anna.mueller@example.com",
        phone="+43 123 456789",
        person_type=PersonType.applicant,
        status=PersonStatus.active,
    )

    employee_person = Person(
        id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        first_name="Thomas",
        last_name="Weber",
        email="thomas.weber@nexurve.com",
        phone="+43 234 567890",
        person_type=PersonType.employee,
        status=PersonStatus.active,
    )

    manager_person = Person(
        id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
        first_name="Sandra",
        last_name="Hofer",
        email="sandra.hofer@nexurve.com",
        phone="+43 345 678901",
        person_type=PersonType.employee,
        status=PersonStatus.active,
    )

    alumni_person = Person(
        id=uuid.UUID("00000000-0000-0000-0000-000000000004"),
        first_name="Max",
        last_name="Berger",
        email="max.berger@alumni.nexurve.com",
        phone=None,
        person_type=PersonType.alumni,
        status=PersonStatus.archived,
    )

    db.add_all([applicant, manager_person, employee_person, alumni_person])
    db.flush()

    # ── Employee Profiles ─────────────────────────────────────────────────────
    manager_profile = EmployeeProfile(
        id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
        person_id=manager_person.id,
        department="Engineering",
        role="Engineering Lead",
        start_date=date(2022, 1, 15),
        end_date=None,
        manager_id=None,
        skills=["Python", "FastAPI", "Leadership", "Architecture"],
        knowledge_areas=["Backend Development", "Team Management", "CI/CD"],
        it_access_level=ITAccessLevel.admin,
    )

    employee_profile = EmployeeProfile(
        id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
        person_id=employee_person.id,
        department="Engineering",
        role="Backend Developer",
        start_date=date(2024, 3, 1),
        end_date=None,
        manager_id=manager_profile.id,
        skills=["Python", "SQLAlchemy", "PostgreSQL", "Docker"],
        knowledge_areas=["Database Design", "API Development"],
        it_access_level=ITAccessLevel.standard,
    )

    alumni_profile = EmployeeProfile(
        id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
        person_id=alumni_person.id,
        department="Sales",
        role="Sales Manager",
        start_date=date(2021, 6, 1),
        end_date=date(2025, 12, 31),
        manager_id=None,
        skills=["CRM", "Negotiation", "B2B Sales"],
        knowledge_areas=["Sales Process", "Key Account Management"],
        it_access_level=ITAccessLevel.none,
    )

    db.add_all([manager_profile, employee_profile, alumni_profile])
    db.flush()

    # ── Documents ─────────────────────────────────────────────────────────────
    db.add_all([
        Document(
            person_id=applicant.id,
            doc_type="cv",
            file_path="/uploads/applicants/anna-mueller-cv.pdf",
            file_name="anna-mueller-cv.pdf",
            extracted_text="Anna Müller – Lebenslauf. 5 Jahre Erfahrung in Python-Entwicklung...",
            vector_id=None,
            processed_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
        ),
        Document(
            person_id=employee_person.id,
            doc_type="contract",
            file_path="/uploads/employees/thomas-weber-contract.pdf",
            file_name="thomas-weber-vertrag.pdf",
            extracted_text=None,
            vector_id=None,
        ),
        Document(
            person_id=alumni_person.id,
            doc_type="certificate",
            file_path="/uploads/alumni/max-berger-zeugnis.pdf",
            file_name="max-berger-arbeitszeugnis.pdf",
            extracted_text="Arbeitszeugnis für Max Berger. Herr Berger war vom 01.06.2021...",
            vector_id=None,
            processed_at=datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc),
        ),
    ])

    # ── Knowledge Entries ─────────────────────────────────────────────────────
    db.add_all([
        KnowledgeEntry(
            author_id=manager_person.id,
            entry_type=EntryType.interview,
            content="Interview mit Max Berger – Wissenstransfer Sales-Prozesse. "
                    "Wichtige Erkenntnisse: Key Account A wird von Maria Schmidt übernommen. "
                    "CRM-Daten sind aktuell. Offene Angebote wurden dokumentiert.",
            summary="Wissenstransfer Sales: Key Account Übergabe + CRM-Status dokumentiert.",
            vector_id=None,
            tags=["offboarding", "sales", "wissenstransfer", "max-berger"],
        ),
        KnowledgeEntry(
            author_id=employee_person.id,
            entry_type=EntryType.protocol,
            content="Deployment-Protokoll v1.2 – Backend-Migration auf PostgreSQL 16. "
                    "Alle Migrationen erfolgreich. Performance-Tests bestanden. "
                    "Downtime: 12 Minuten. Rollback-Plan war vorbereitet.",
            summary="Deployment v1.2 erfolgreich – PostgreSQL 16 Migration abgeschlossen.",
            vector_id=None,
            tags=["deployment", "postgresql", "migration", "protokoll"],
        ),
    ])

    # ── Onboarding Tasks ──────────────────────────────────────────────────────
    db.add_all([
        OnboardingTask(
            employee_id=employee_profile.id,
            task_type="it_setup",
            status=TaskStatus.completed,
            due_date=date(2024, 3, 5),
            completed_at=datetime(2024, 3, 4, 10, 0, tzinfo=timezone.utc),
            assigned_to=manager_profile.person_id,
        ),
        OnboardingTask(
            employee_id=employee_profile.id,
            task_type="document_upload",
            status=TaskStatus.completed,
            due_date=date(2024, 3, 3),
            completed_at=datetime(2024, 3, 2, 15, 30, tzinfo=timezone.utc),
            assigned_to=None,
        ),
        OnboardingTask(
            employee_id=employee_profile.id,
            task_type="intro_meeting",
            status=TaskStatus.completed,
            due_date=date(2024, 3, 7),
            completed_at=datetime(2024, 3, 7, 9, 0, tzinfo=timezone.utc),
            assigned_to=manager_profile.person_id,
        ),
    ])

    # ── Offboarding Plan ──────────────────────────────────────────────────────
    db.add(OffboardingPlan(
        employee_id=alumni_profile.id,
        trigger_date=date(2025, 10, 1),
        last_day=date(2025, 12, 31),
        knowledge_extraction_score=0.87,
        weekly_interview_schedule=[
            {"week": 1, "date": "2025-11-03", "topics": ["Sales-Prozesse", "Key Accounts"], "done": True},
            {"week": 2, "date": "2025-11-10", "topics": ["CRM-Daten", "Offene Angebote"], "done": True},
            {"week": 3, "date": "2025-11-17", "topics": ["Partnerschaften", "Reporting"], "done": True},
            {"week": 4, "date": "2025-11-24", "topics": ["Abschlussbesprechung"], "done": True},
        ],
    ))

    # ── Audit Log ─────────────────────────────────────────────────────────────
    db.add_all([
        AuditLog(
            action=AuditAction.CREATE,
            entity_type="Person",
            entity_id=applicant.id,
            performed_by=None,
            ip_address="192.168.1.100",
            extra_data={"source": "application_form"},
        ),
        AuditLog(
            action=AuditAction.CREATE,
            entity_type="EmployeeProfile",
            entity_id=employee_profile.id,
            performed_by=manager_person.id,
            ip_address="10.0.0.5",
        ),
        AuditLog(
            action=AuditAction.UPDATE,
            entity_type="EmployeeProfile",
            entity_id=employee_profile.id,
            performed_by=manager_person.id,
            ip_address="10.0.0.5",
            extra_data={"changed_fields": ["it_access_level"], "old_value": "basic", "new_value": "standard"},
        ),
        AuditLog(
            action=AuditAction.VIEW,
            entity_type="Document",
            entity_id=applicant.id,
            performed_by=manager_person.id,
            ip_address="10.0.0.5",
        ),
        AuditLog(
            action=AuditAction.EXPORT,
            entity_type="Person",
            entity_id=alumni_person.id,
            performed_by=manager_person.id,
            ip_address="10.0.0.5",
            extra_data={"reason": "DSGVO-Auskunftsbegehren", "format": "json"},
        ),
    ])

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    print("✅ Seed data created successfully.")
    print(f"   Persons:          4")
    print(f"   EmployeeProfiles: 3")
    print(f"   Documents:        3")
    print(f"   KnowledgeEntries: 2")
    print(f"   OnboardingTasks:  3")
    print(f"   OffboardingPlans: 1")
    print(f"   AuditLog:         5")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
