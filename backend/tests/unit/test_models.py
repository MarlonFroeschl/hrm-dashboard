"""Unit tests for HRM Lifecycle database schema models.

Tests are purely structural – no live database connection required.
SQLAlchemy table metadata, enum definitions and relationship attributes
are inspected directly on the model/table objects.

Coverage:
- Enum values: PersonType, PersonStatus, ITAccessLevel, EntryType, TaskStatus
- Table names for all 7 models
- Required columns existence per model
- Nullable vs. non-nullable constraints on selected columns
- Server defaults and Python-level defaults
- Indexes (single-column and composite)
- Relationship attributes on model classes
- Foreign key targets
- seed_database() skip-logic via mock
"""

from unittest.mock import MagicMock

from app.models.audit_log import AuditLog
from app.models.document import Document
from app.models.employee_profile import EmployeeProfile, ITAccessLevel
from app.models.knowledge_entry import EntryType, KnowledgeEntry
from app.models.offboarding_plan import OffboardingPlan
from app.models.onboarding_task import OnboardingTask, TaskStatus
from app.models.person import Person, PersonStatus, PersonType


# ---------------------------------------------------------------------------
# 1. Enum tests
# ---------------------------------------------------------------------------


class TestPersonTypeEnum:
    def test_applicant_value(self):
        assert PersonType.applicant.value == "applicant"

    def test_employee_value(self):
        assert PersonType.employee.value == "employee"

    def test_alumni_value(self):
        assert PersonType.alumni.value == "alumni"

    def test_total_member_count(self):
        assert len(PersonType) == 3


class TestPersonStatusEnum:
    def test_active_value(self):
        assert PersonStatus.active.value == "active"

    def test_onboarding_value(self):
        assert PersonStatus.onboarding.value == "onboarding"

    def test_offboarding_value(self):
        assert PersonStatus.offboarding.value == "offboarding"

    def test_archived_value(self):
        assert PersonStatus.archived.value == "archived"

    def test_total_member_count(self):
        assert len(PersonStatus) == 4


class TestITAccessLevelEnum:
    def test_none_value(self):
        assert ITAccessLevel.none.value == "none"

    def test_basic_value(self):
        assert ITAccessLevel.basic.value == "basic"

    def test_standard_value(self):
        assert ITAccessLevel.standard.value == "standard"

    def test_admin_value(self):
        assert ITAccessLevel.admin.value == "admin"

    def test_total_member_count(self):
        assert len(ITAccessLevel) == 4


class TestEntryTypeEnum:
    def test_voice_note_value(self):
        assert EntryType.voice_note.value == "voice_note"

    def test_interview_value(self):
        assert EntryType.interview.value == "interview"

    def test_document_value(self):
        assert EntryType.document.value == "document"

    def test_protocol_value(self):
        assert EntryType.protocol.value == "protocol"

    def test_total_member_count(self):
        assert len(EntryType) == 4


class TestTaskStatusEnum:
    def test_pending_value(self):
        assert TaskStatus.pending.value == "pending"

    def test_in_progress_value(self):
        assert TaskStatus.in_progress.value == "in_progress"

    def test_completed_value(self):
        assert TaskStatus.completed.value == "completed"

    def test_skipped_value(self):
        assert TaskStatus.skipped.value == "skipped"

    def test_total_member_count(self):
        assert len(TaskStatus) == 4


# ---------------------------------------------------------------------------
# 2. Table name tests
# ---------------------------------------------------------------------------


class TestTableNames:
    def test_person_tablename(self):
        assert Person.__tablename__ == "persons"

    def test_employee_profile_tablename(self):
        assert EmployeeProfile.__tablename__ == "employee_profiles"

    def test_document_tablename(self):
        assert Document.__tablename__ == "documents"

    def test_knowledge_entry_tablename(self):
        assert KnowledgeEntry.__tablename__ == "knowledge_entries"

    def test_onboarding_task_tablename(self):
        assert OnboardingTask.__tablename__ == "onboarding_tasks"

    def test_offboarding_plan_tablename(self):
        assert OffboardingPlan.__tablename__ == "offboarding_plans"

    def test_audit_log_tablename(self):
        assert AuditLog.__tablename__ == "audit_log"


# ---------------------------------------------------------------------------
# 3. Required column existence tests
# ---------------------------------------------------------------------------


class TestPersonColumns:
    def test_has_id_column(self):
        assert "id" in Person.__table__.c

    def test_has_first_name_column(self):
        assert "first_name" in Person.__table__.c

    def test_has_last_name_column(self):
        assert "last_name" in Person.__table__.c

    def test_has_email_column(self):
        assert "email" in Person.__table__.c

    def test_has_phone_column(self):
        assert "phone" in Person.__table__.c

    def test_has_person_type_column(self):
        assert "person_type" in Person.__table__.c

    def test_has_status_column(self):
        assert "status" in Person.__table__.c

    def test_has_created_at_column(self):
        assert "created_at" in Person.__table__.c

    def test_has_updated_at_column(self):
        assert "updated_at" in Person.__table__.c


class TestEmployeeProfileColumns:
    def test_has_id_column(self):
        assert "id" in EmployeeProfile.__table__.c

    def test_has_person_id_column(self):
        assert "person_id" in EmployeeProfile.__table__.c

    def test_has_department_column(self):
        assert "department" in EmployeeProfile.__table__.c

    def test_has_role_column(self):
        assert "role" in EmployeeProfile.__table__.c

    def test_has_start_date_column(self):
        assert "start_date" in EmployeeProfile.__table__.c

    def test_has_end_date_column(self):
        assert "end_date" in EmployeeProfile.__table__.c

    def test_has_manager_id_column(self):
        assert "manager_id" in EmployeeProfile.__table__.c

    def test_has_skills_column(self):
        assert "skills" in EmployeeProfile.__table__.c

    def test_has_knowledge_areas_column(self):
        assert "knowledge_areas" in EmployeeProfile.__table__.c

    def test_has_it_access_level_column(self):
        assert "it_access_level" in EmployeeProfile.__table__.c


class TestDocumentColumns:
    def test_has_id_column(self):
        assert "id" in Document.__table__.c

    def test_has_person_id_column(self):
        assert "person_id" in Document.__table__.c

    def test_has_doc_type_column(self):
        assert "doc_type" in Document.__table__.c

    def test_has_file_path_column(self):
        assert "file_path" in Document.__table__.c

    def test_has_file_name_column(self):
        assert "file_name" in Document.__table__.c

    def test_has_extracted_text_column(self):
        assert "extracted_text" in Document.__table__.c

    def test_has_vector_id_column(self):
        assert "vector_id" in Document.__table__.c

    def test_has_processed_at_column(self):
        assert "processed_at" in Document.__table__.c


class TestKnowledgeEntryColumns:
    def test_has_id_column(self):
        assert "id" in KnowledgeEntry.__table__.c

    def test_has_author_id_column(self):
        assert "author_id" in KnowledgeEntry.__table__.c

    def test_has_entry_type_column(self):
        assert "entry_type" in KnowledgeEntry.__table__.c

    def test_has_content_column(self):
        assert "content" in KnowledgeEntry.__table__.c

    def test_has_summary_column(self):
        assert "summary" in KnowledgeEntry.__table__.c

    def test_has_tags_column(self):
        assert "tags" in KnowledgeEntry.__table__.c

    def test_has_vector_id_column(self):
        assert "vector_id" in KnowledgeEntry.__table__.c


class TestOnboardingTaskColumns:
    def test_has_id_column(self):
        assert "id" in OnboardingTask.__table__.c

    def test_has_employee_id_column(self):
        assert "employee_id" in OnboardingTask.__table__.c

    def test_has_task_type_column(self):
        assert "task_type" in OnboardingTask.__table__.c

    def test_has_status_column(self):
        assert "status" in OnboardingTask.__table__.c

    def test_has_due_date_column(self):
        assert "due_date" in OnboardingTask.__table__.c

    def test_has_completed_at_column(self):
        assert "completed_at" in OnboardingTask.__table__.c

    def test_has_assigned_to_column(self):
        assert "assigned_to" in OnboardingTask.__table__.c


class TestOffboardingPlanColumns:
    def test_has_id_column(self):
        assert "id" in OffboardingPlan.__table__.c

    def test_has_employee_id_column(self):
        assert "employee_id" in OffboardingPlan.__table__.c

    def test_has_trigger_date_column(self):
        assert "trigger_date" in OffboardingPlan.__table__.c

    def test_has_last_day_column(self):
        assert "last_day" in OffboardingPlan.__table__.c

    def test_has_knowledge_extraction_score_column(self):
        assert "knowledge_extraction_score" in OffboardingPlan.__table__.c

    def test_has_weekly_interview_schedule_column(self):
        assert "weekly_interview_schedule" in OffboardingPlan.__table__.c


class TestAuditLogColumns:
    def test_has_id_column(self):
        assert "id" in AuditLog.__table__.c

    def test_has_action_column(self):
        assert "action" in AuditLog.__table__.c

    def test_has_entity_type_column(self):
        assert "entity_type" in AuditLog.__table__.c

    def test_has_entity_id_column(self):
        assert "entity_id" in AuditLog.__table__.c

    def test_has_performed_by_column(self):
        assert "performed_by" in AuditLog.__table__.c

    def test_has_timestamp_column(self):
        assert "timestamp" in AuditLog.__table__.c

    def test_has_ip_address_column(self):
        assert "ip_address" in AuditLog.__table__.c

    def test_has_extra_data_column(self):
        assert "extra_data" in AuditLog.__table__.c


# ---------------------------------------------------------------------------
# 4. Nullable constraint tests
# ---------------------------------------------------------------------------


class TestPersonNullableConstraints:
    def test_email_is_not_nullable(self):
        assert Person.__table__.c.email.nullable is False

    def test_first_name_is_not_nullable(self):
        assert Person.__table__.c.first_name.nullable is False

    def test_last_name_is_not_nullable(self):
        assert Person.__table__.c.last_name.nullable is False

    def test_person_type_is_not_nullable(self):
        assert Person.__table__.c.person_type.nullable is False

    def test_status_is_not_nullable(self):
        assert Person.__table__.c.status.nullable is False

    def test_phone_is_nullable(self):
        assert Person.__table__.c.phone.nullable is True


class TestEmployeeProfileNullableConstraints:
    def test_department_is_not_nullable(self):
        assert EmployeeProfile.__table__.c.department.nullable is False

    def test_role_is_not_nullable(self):
        assert EmployeeProfile.__table__.c.role.nullable is False

    def test_start_date_is_not_nullable(self):
        assert EmployeeProfile.__table__.c.start_date.nullable is False

    def test_end_date_is_nullable(self):
        assert EmployeeProfile.__table__.c.end_date.nullable is True

    def test_manager_id_is_nullable(self):
        assert EmployeeProfile.__table__.c.manager_id.nullable is True


class TestDocumentNullableConstraints:
    def test_person_id_is_not_nullable(self):
        assert Document.__table__.c.person_id.nullable is False

    def test_doc_type_is_not_nullable(self):
        assert Document.__table__.c.doc_type.nullable is False

    def test_file_path_is_not_nullable(self):
        assert Document.__table__.c.file_path.nullable is False

    def test_extracted_text_is_nullable(self):
        assert Document.__table__.c.extracted_text.nullable is True

    def test_vector_id_is_nullable(self):
        assert Document.__table__.c.vector_id.nullable is True

    def test_processed_at_is_nullable(self):
        assert Document.__table__.c.processed_at.nullable is True


class TestAuditLogNullableConstraints:
    def test_action_is_not_nullable(self):
        assert AuditLog.__table__.c.action.nullable is False

    def test_entity_type_is_not_nullable(self):
        assert AuditLog.__table__.c.entity_type.nullable is False

    def test_entity_id_is_not_nullable(self):
        assert AuditLog.__table__.c.entity_id.nullable is False

    def test_performed_by_is_nullable(self):
        # performed_by can be NULL when triggered by system actions
        assert AuditLog.__table__.c.performed_by.nullable is True

    def test_ip_address_is_nullable(self):
        assert AuditLog.__table__.c.ip_address.nullable is True

    def test_extra_data_is_nullable(self):
        assert AuditLog.__table__.c.extra_data.nullable is True


class TestOnboardingTaskNullableConstraints:
    def test_employee_id_is_not_nullable(self):
        assert OnboardingTask.__table__.c.employee_id.nullable is False

    def test_task_type_is_not_nullable(self):
        assert OnboardingTask.__table__.c.task_type.nullable is False

    def test_status_is_not_nullable(self):
        assert OnboardingTask.__table__.c.status.nullable is False

    def test_due_date_is_nullable(self):
        assert OnboardingTask.__table__.c.due_date.nullable is True

    def test_completed_at_is_nullable(self):
        assert OnboardingTask.__table__.c.completed_at.nullable is True

    def test_assigned_to_is_nullable(self):
        assert OnboardingTask.__table__.c.assigned_to.nullable is True


class TestOffboardingPlanNullableConstraints:
    def test_employee_id_is_not_nullable(self):
        assert OffboardingPlan.__table__.c.employee_id.nullable is False

    def test_trigger_date_is_not_nullable(self):
        assert OffboardingPlan.__table__.c.trigger_date.nullable is False

    def test_last_day_is_not_nullable(self):
        assert OffboardingPlan.__table__.c.last_day.nullable is False

    def test_knowledge_extraction_score_is_nullable(self):
        assert OffboardingPlan.__table__.c.knowledge_extraction_score.nullable is True


# ---------------------------------------------------------------------------
# 5. Default value tests
# ---------------------------------------------------------------------------


class TestDefaultValues:
    def test_person_status_has_server_default_active(self):
        col = Person.__table__.c.status
        assert col.server_default is not None
        assert "active" in str(col.server_default.arg)

    def test_onboarding_task_status_has_server_default_pending(self):
        col = OnboardingTask.__table__.c.status
        assert col.server_default is not None
        assert "pending" in str(col.server_default.arg)

    def test_employee_profile_it_access_level_has_server_default_none(self):
        col = EmployeeProfile.__table__.c.it_access_level
        assert col.server_default is not None
        assert "none" in str(col.server_default.arg)

    def test_employee_profile_skills_has_server_default_empty_list(self):
        col = EmployeeProfile.__table__.c.skills
        assert col.server_default is not None
        assert "[]" in str(col.server_default.arg)

    def test_employee_profile_knowledge_areas_has_server_default_empty_list(self):
        col = EmployeeProfile.__table__.c.knowledge_areas
        assert col.server_default is not None
        assert "[]" in str(col.server_default.arg)

    def test_knowledge_entry_tags_has_server_default_empty_list(self):
        col = KnowledgeEntry.__table__.c.tags
        assert col.server_default is not None
        assert "[]" in str(col.server_default.arg)

    def test_offboarding_plan_weekly_interview_schedule_has_server_default(self):
        col = OffboardingPlan.__table__.c.weekly_interview_schedule
        assert col.server_default is not None
        assert "[]" in str(col.server_default.arg)


# ---------------------------------------------------------------------------
# 6. Index tests
# ---------------------------------------------------------------------------


class TestPersonIndexes:
    def _index_names(self):
        return {idx.name for idx in Person.__table__.indexes}

    def test_has_person_type_index(self):
        assert "idx_persons_person_type" in self._index_names()

    def test_has_status_index(self):
        assert "idx_persons_status" in self._index_names()

    def test_has_created_at_index(self):
        assert "idx_persons_created_at" in self._index_names()

    def test_email_column_is_unique(self):
        assert Person.__table__.c.email.unique is True


class TestEmployeeProfileIndexes:
    def _index_names(self):
        return {idx.name for idx in EmployeeProfile.__table__.indexes}

    def test_has_department_index(self):
        assert "idx_employee_profiles_department" in self._index_names()

    def test_has_manager_id_index(self):
        assert "idx_employee_profiles_manager_id" in self._index_names()

    def test_has_start_date_index(self):
        assert "idx_employee_profiles_start_date" in self._index_names()

    def test_person_id_column_is_unique(self):
        # One-to-one: a person can have at most one employee profile
        assert EmployeeProfile.__table__.c.person_id.unique is True


class TestDocumentIndexes:
    def _index_names(self):
        return {idx.name for idx in Document.__table__.indexes}

    def test_has_person_id_index(self):
        assert "idx_documents_person_id" in self._index_names()

    def test_has_doc_type_index(self):
        assert "idx_documents_doc_type" in self._index_names()

    def test_has_vector_id_index(self):
        assert "idx_documents_vector_id" in self._index_names()

    def test_has_processed_at_index(self):
        assert "idx_documents_processed_at" in self._index_names()


class TestKnowledgeEntryIndexes:
    def _index_names(self):
        return {idx.name for idx in KnowledgeEntry.__table__.indexes}

    def test_has_author_id_index(self):
        assert "idx_knowledge_entries_author_id" in self._index_names()

    def test_has_entry_type_index(self):
        assert "idx_knowledge_entries_entry_type" in self._index_names()

    def test_has_vector_id_index(self):
        assert "idx_knowledge_entries_vector_id" in self._index_names()

    def test_has_created_at_index(self):
        assert "idx_knowledge_entries_created_at" in self._index_names()


class TestOnboardingTaskIndexes:
    def _index_names(self):
        return {idx.name for idx in OnboardingTask.__table__.indexes}

    def test_has_employee_id_index(self):
        assert "idx_onboarding_tasks_employee_id" in self._index_names()

    def test_has_status_index(self):
        assert "idx_onboarding_tasks_status" in self._index_names()

    def test_has_due_date_index(self):
        assert "idx_onboarding_tasks_due_date" in self._index_names()


class TestOffboardingPlanIndexes:
    def _index_names(self):
        return {idx.name for idx in OffboardingPlan.__table__.indexes}

    def test_has_employee_id_index(self):
        assert "idx_offboarding_plans_employee_id" in self._index_names()

    def test_has_last_day_index(self):
        assert "idx_offboarding_plans_last_day" in self._index_names()

    def test_has_trigger_date_index(self):
        assert "idx_offboarding_plans_trigger_date" in self._index_names()


class TestAuditLogIndexes:
    def _index_names(self):
        return {idx.name for idx in AuditLog.__table__.indexes}

    def test_has_performed_by_index(self):
        assert "idx_audit_log_performed_by" in self._index_names()

    def test_has_timestamp_index(self):
        assert "idx_audit_log_timestamp" in self._index_names()

    def test_has_action_index(self):
        assert "idx_audit_log_action" in self._index_names()

    def test_has_composite_entity_index(self):
        assert "idx_audit_log_entity" in self._index_names()

    def test_composite_entity_index_covers_two_columns(self):
        entity_index = next(
            idx for idx in AuditLog.__table__.indexes if idx.name == "idx_audit_log_entity"
        )
        assert len(list(entity_index.columns)) == 2

    def test_composite_entity_index_contains_entity_type(self):
        entity_index = next(
            idx for idx in AuditLog.__table__.indexes if idx.name == "idx_audit_log_entity"
        )
        column_names = {col.name for col in entity_index.columns}
        assert "entity_type" in column_names

    def test_composite_entity_index_contains_entity_id(self):
        entity_index = next(
            idx for idx in AuditLog.__table__.indexes if idx.name == "idx_audit_log_entity"
        )
        column_names = {col.name for col in entity_index.columns}
        assert "entity_id" in column_names


# ---------------------------------------------------------------------------
# 7. Relationship attribute tests
# ---------------------------------------------------------------------------


class TestPersonRelationships:
    def test_has_employee_profile_relationship(self):
        assert hasattr(Person, "employee_profile")

    def test_has_documents_relationship(self):
        assert hasattr(Person, "documents")

    def test_has_knowledge_entries_relationship(self):
        assert hasattr(Person, "knowledge_entries")

    def test_has_audit_logs_performed_relationship(self):
        assert hasattr(Person, "audit_logs_performed")


class TestEmployeeProfileRelationships:
    def test_has_person_relationship(self):
        assert hasattr(EmployeeProfile, "person")

    def test_has_self_referencing_manager_relationship(self):
        assert hasattr(EmployeeProfile, "manager")

    def test_has_direct_reports_relationship(self):
        assert hasattr(EmployeeProfile, "direct_reports")

    def test_has_onboarding_tasks_relationship(self):
        assert hasattr(EmployeeProfile, "onboarding_tasks")

    def test_has_offboarding_plans_relationship(self):
        assert hasattr(EmployeeProfile, "offboarding_plans")


class TestDocumentRelationships:
    def test_has_person_relationship(self):
        assert hasattr(Document, "person")


class TestKnowledgeEntryRelationships:
    def test_has_author_relationship(self):
        assert hasattr(KnowledgeEntry, "author")


class TestOnboardingTaskRelationships:
    def test_has_employee_relationship(self):
        assert hasattr(OnboardingTask, "employee")


class TestOffboardingPlanRelationships:
    def test_has_employee_relationship(self):
        assert hasattr(OffboardingPlan, "employee")


class TestAuditLogRelationships:
    def test_has_performer_relationship(self):
        assert hasattr(AuditLog, "performer")


# ---------------------------------------------------------------------------
# 8. Foreign key tests
# ---------------------------------------------------------------------------


class TestForeignKeys:
    def test_employee_profile_person_id_references_persons(self):
        fk = list(EmployeeProfile.__table__.c.person_id.foreign_keys)[0]
        assert "persons.id" in str(fk.target_fullname)

    def test_employee_profile_manager_id_references_itself(self):
        fk = list(EmployeeProfile.__table__.c.manager_id.foreign_keys)[0]
        assert "employee_profiles.id" in str(fk.target_fullname)

    def test_document_person_id_references_persons(self):
        fk = list(Document.__table__.c.person_id.foreign_keys)[0]
        assert "persons.id" in str(fk.target_fullname)

    def test_knowledge_entry_author_id_references_persons(self):
        fk = list(KnowledgeEntry.__table__.c.author_id.foreign_keys)[0]
        assert "persons.id" in str(fk.target_fullname)

    def test_onboarding_task_employee_id_references_employee_profiles(self):
        fk = list(OnboardingTask.__table__.c.employee_id.foreign_keys)[0]
        assert "employee_profiles.id" in str(fk.target_fullname)

    def test_offboarding_plan_employee_id_references_employee_profiles(self):
        fk = list(OffboardingPlan.__table__.c.employee_id.foreign_keys)[0]
        assert "employee_profiles.id" in str(fk.target_fullname)

    def test_audit_log_performed_by_references_persons(self):
        fk = list(AuditLog.__table__.c.performed_by.foreign_keys)[0]
        assert "persons.id" in str(fk.target_fullname)

    def test_document_person_id_cascades_on_delete(self):
        fk = list(Document.__table__.c.person_id.foreign_keys)[0]
        assert fk.ondelete.upper() == "CASCADE"

    def test_knowledge_entry_author_id_restricts_on_delete(self):
        fk = list(KnowledgeEntry.__table__.c.author_id.foreign_keys)[0]
        assert fk.ondelete.upper() == "RESTRICT"

    def test_audit_log_performed_by_sets_null_on_delete(self):
        fk = list(AuditLog.__table__.c.performed_by.foreign_keys)[0]
        assert fk.ondelete.upper() == "SET NULL"

    def test_onboarding_task_employee_id_cascades_on_delete(self):
        fk = list(OnboardingTask.__table__.c.employee_id.foreign_keys)[0]
        assert fk.ondelete.upper() == "CASCADE"

    def test_offboarding_plan_employee_id_cascades_on_delete(self):
        fk = list(OffboardingPlan.__table__.c.employee_id.foreign_keys)[0]
        assert fk.ondelete.upper() == "CASCADE"

    def test_employee_profile_manager_id_sets_null_on_delete(self):
        fk = list(EmployeeProfile.__table__.c.manager_id.foreign_keys)[0]
        assert fk.ondelete.upper() == "SET NULL"


# ---------------------------------------------------------------------------
# 9. Primary key tests
# ---------------------------------------------------------------------------


class TestPrimaryKeys:
    def test_person_id_is_primary_key(self):
        assert Person.__table__.c.id.primary_key is True

    def test_employee_profile_id_is_primary_key(self):
        assert EmployeeProfile.__table__.c.id.primary_key is True

    def test_document_id_is_primary_key(self):
        assert Document.__table__.c.id.primary_key is True

    def test_knowledge_entry_id_is_primary_key(self):
        assert KnowledgeEntry.__table__.c.id.primary_key is True

    def test_onboarding_task_id_is_primary_key(self):
        assert OnboardingTask.__table__.c.id.primary_key is True

    def test_offboarding_plan_id_is_primary_key(self):
        assert OffboardingPlan.__table__.c.id.primary_key is True

    def test_audit_log_id_is_primary_key(self):
        assert AuditLog.__table__.c.id.primary_key is True


# ---------------------------------------------------------------------------
# 10. __repr__ tests
# ---------------------------------------------------------------------------


class TestReprMethods:
    def test_person_repr_contains_classname(self):
        p = Person.__new__(Person)
        p.id = "test-id"
        p.email = "test@example.com"
        p.person_type = PersonType.employee
        assert "Person" in repr(p)

    def test_employee_profile_repr_contains_classname(self):
        ep = EmployeeProfile.__new__(EmployeeProfile)
        ep.id = "test-id"
        ep.role = "Developer"
        ep.department = "Engineering"
        assert "EmployeeProfile" in repr(ep)

    def test_onboarding_task_repr_contains_classname(self):
        t = OnboardingTask.__new__(OnboardingTask)
        t.id = "test-id"
        t.task_type = "it_setup"
        t.status = TaskStatus.pending
        assert "OnboardingTask" in repr(t)

    def test_audit_log_repr_contains_classname(self):
        a = AuditLog.__new__(AuditLog)
        a.id = "test-id"
        a.action = "CREATE"
        a.entity_type = "Person"
        a.entity_id = "entity-id"
        assert "AuditLog" in repr(a)


# ---------------------------------------------------------------------------
# 11. Seed function tests (mock-based, no DB)
# ---------------------------------------------------------------------------


class TestSeedDatabase:
    def test_seed_skips_when_data_already_exists(self):
        """seed_database() must be idempotent: no inserts if persons exist."""
        from app.db.seed import seed_database

        db = MagicMock()
        db.query.return_value.count.return_value = 5

        seed_database(db)

        db.add.assert_not_called()
        db.add_all.assert_not_called()

    def test_seed_does_not_commit_when_data_already_exists(self):
        from app.db.seed import seed_database

        db = MagicMock()
        db.query.return_value.count.return_value = 3

        seed_database(db)

        db.commit.assert_not_called()

    def test_seed_queries_person_table_for_existence_check(self):
        from app.db.seed import seed_database

        db = MagicMock()
        db.query.return_value.count.return_value = 1

        seed_database(db)

        db.query.assert_called_once_with(Person)

    def test_seed_calls_add_all_when_table_is_empty(self):
        """seed_database() must insert data when Person count is 0."""
        from app.db.seed import seed_database

        db = MagicMock()
        db.query.return_value.count.return_value = 0

        seed_database(db)

        assert db.add_all.called or db.add.called

    def test_seed_commits_when_table_is_empty(self):
        from app.db.seed import seed_database

        db = MagicMock()
        db.query.return_value.count.return_value = 0

        seed_database(db)

        db.commit.assert_called_once()
