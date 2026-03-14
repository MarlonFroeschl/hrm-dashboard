"""Initial lifecycle schema

Revision ID: 001
Revises:
Create Date: 2026-03-14

Tables: persons, employee_profiles, documents, knowledge_entries,
        onboarding_tasks, offboarding_plans, audit_log
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUMs ─────────────────────────────────────────────────────────────────
    person_type_enum = postgresql.ENUM(
        "applicant", "employee", "alumni",
        name="persontype", create_type=True
    )
    person_status_enum = postgresql.ENUM(
        "active", "onboarding", "offboarding", "archived",
        name="personstatus", create_type=True
    )
    it_access_level_enum = postgresql.ENUM(
        "none", "basic", "standard", "admin",
        name="itaccesslevel", create_type=True
    )
    entry_type_enum = postgresql.ENUM(
        "voice_note", "interview", "document", "protocol",
        name="entrytype", create_type=True
    )
    task_status_enum = postgresql.ENUM(
        "pending", "in_progress", "completed", "skipped",
        name="taskstatus", create_type=True
    )
    audit_action_enum = postgresql.ENUM(
        "CREATE", "UPDATE", "DELETE", "VIEW", "EXPORT", "LOGIN", "LOGOUT",
        name="auditaction", create_type=True
    )

    person_type_enum.create(op.get_bind(), checkfirst=True)
    person_status_enum.create(op.get_bind(), checkfirst=True)
    it_access_level_enum.create(op.get_bind(), checkfirst=True)
    entry_type_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)
    audit_action_enum.create(op.get_bind(), checkfirst=True)

    # ── persons ───────────────────────────────────────────────────────────────
    op.create_table(
        "persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("person_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_persons_email", "persons", ["email"], unique=True)
    op.create_index("idx_persons_person_type", "persons", ["person_type"])
    op.create_index("idx_persons_status", "persons", ["status"])
    op.create_index("idx_persons_created_at", "persons", ["created_at"])

    # ── employee_profiles ─────────────────────────────────────────────────────
    op.create_table(
        "employee_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "person_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("persons.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("role", sa.String(150), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column(
            "manager_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employee_profiles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("skills", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("knowledge_areas", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "it_access_level",
            sa.String(20),
            nullable=False,
            server_default="none",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_employee_profiles_person_id", "employee_profiles", ["person_id"], unique=True
    )
    op.create_index("idx_employee_profiles_department", "employee_profiles", ["department"])
    op.create_index("idx_employee_profiles_manager_id", "employee_profiles", ["manager_id"])
    op.create_index("idx_employee_profiles_start_date", "employee_profiles", ["start_date"])

    # ── documents ─────────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "person_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("persons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("doc_type", sa.String(100), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("vector_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_documents_person_id", "documents", ["person_id"])
    op.create_index("idx_documents_doc_type", "documents", ["doc_type"])
    op.create_index("idx_documents_vector_id", "documents", ["vector_id"])
    op.create_index("idx_documents_processed_at", "documents", ["processed_at"])

    # ── knowledge_entries ─────────────────────────────────────────────────────
    op.create_table(
        "knowledge_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "author_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("persons.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("entry_type", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("vector_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_knowledge_entries_author_id", "knowledge_entries", ["author_id"])
    op.create_index("idx_knowledge_entries_entry_type", "knowledge_entries", ["entry_type"])
    op.create_index("idx_knowledge_entries_vector_id", "knowledge_entries", ["vector_id"])
    op.create_index("idx_knowledge_entries_created_at", "knowledge_entries", ["created_at"])

    # ── onboarding_tasks ──────────────────────────────────────────────────────
    op.create_table(
        "onboarding_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employee_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("task_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_onboarding_tasks_employee_id", "onboarding_tasks", ["employee_id"])
    op.create_index("idx_onboarding_tasks_status", "onboarding_tasks", ["status"])
    op.create_index("idx_onboarding_tasks_due_date", "onboarding_tasks", ["due_date"])

    # ── offboarding_plans ─────────────────────────────────────────────────────
    op.create_table(
        "offboarding_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employee_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("trigger_date", sa.Date, nullable=False),
        sa.Column("last_day", sa.Date, nullable=False),
        sa.Column("knowledge_extraction_score", sa.Float, nullable=True),
        sa.Column(
            "weekly_interview_schedule",
            postgresql.JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_offboarding_plans_employee_id", "offboarding_plans", ["employee_id"])
    op.create_index("idx_offboarding_plans_last_day", "offboarding_plans", ["last_day"])
    op.create_index("idx_offboarding_plans_trigger_date", "offboarding_plans", ["trigger_date"])

    # ── audit_log ─────────────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "performed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("persons.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("extra_data", postgresql.JSONB, nullable=True),
    )
    op.create_index(
        "idx_audit_log_entity", "audit_log", ["entity_type", "entity_id"]
    )
    op.create_index("idx_audit_log_performed_by", "audit_log", ["performed_by"])
    op.create_index("idx_audit_log_timestamp", "audit_log", ["timestamp"])
    op.create_index("idx_audit_log_action", "audit_log", ["action"])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("audit_log")
    op.drop_table("offboarding_plans")
    op.drop_table("onboarding_tasks")
    op.drop_table("knowledge_entries")
    op.drop_table("documents")
    op.drop_table("employee_profiles")
    op.drop_table("persons")

    # Drop ENUMs in reverse creation order
    op.execute(sa.text("DROP TYPE IF EXISTS auditaction"))
    op.execute(sa.text("DROP TYPE IF EXISTS taskstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS entrytype"))
    op.execute(sa.text("DROP TYPE IF EXISTS itaccesslevel"))
    op.execute(sa.text("DROP TYPE IF EXISTS personstatus"))
    op.execute(sa.text("DROP TYPE IF EXISTS persontype"))
