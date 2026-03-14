import asyncio
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.person import Person, PersonStatus, PersonType
from app.schemas.applicant import ApplicantCreate, ApplicantStatusUpdate
from app.services import cv_parser_service, webhook_service
from app.core.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR)

# Accepted MIME types for CV uploads
_ACCEPTED_CV_CONTENT_TYPES = {"application/pdf"}


def _get_person_or_404(db: Session, person_id: UUID) -> Person:
    """Load a Person by id or raise 404."""
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant {person_id} not found",
        )
    return person


def _save_file_sync(destination: Path, content: bytes) -> None:
    """Write file bytes synchronously (called via asyncio.to_thread)."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)


async def create_applicant(db: Session, data: ApplicantCreate) -> Person:
    """Create a new applicant. Raises 409 if email already exists."""
    try:
        existing = db.execute(
            select(Person).where(Person.email == data.email)
        ).scalar_one_or_none()

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {data.email} is already registered",
            )

        person = Person(
            first_name=data.first_name,
            last_name=data.last_name,
            email=str(data.email),
            phone=data.phone,
            person_type=PersonType.applicant,
            status=PersonStatus.active,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        logger.info("Created applicant id=%s", person.id)
        return person
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("Failed to create applicant: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create applicant",
        ) from exc


async def upload_cv_and_parse(db: Session, person_id: UUID, file: UploadFile) -> Document:
    """Save CV file, parse it via Claude, persist Document, trigger webhook."""
    person = _get_person_or_404(db, person_id)

    try:
        if file.content_type not in _ACCEPTED_CV_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are accepted",
            )

        file_content = await file.read()
        if len(file_content) > settings.MAX_CV_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds maximum allowed size",
            )

        safe_filename = Path(file.filename or "cv.pdf").name
        destination = (UPLOAD_DIR / str(person_id) / safe_filename).resolve()
        if not str(destination).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename",
            )

        # Write file in a thread to avoid blocking the event loop
        await asyncio.to_thread(_save_file_sync, destination, file_content)

        raw_text, extracted_data, matching_score = await cv_parser_service.parse_cv(
            str(destination)
        )

        doc = Document(
            person_id=person.id,
            doc_type="cv",
            file_path=str(destination),
            file_name=safe_filename,
            extracted_text=raw_text or None,
            extracted_data=extracted_data.model_dump(),
            matching_score=matching_score,
            processed_at=datetime.now(timezone.utc),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info("CV document id=%s saved for applicant id=%s", doc.id, person_id)

        # Fire-and-forget webhook – hold reference to prevent GC cancellation
        task = asyncio.create_task(
            webhook_service.trigger(
                settings.N8N_WEBHOOK_NEW_APPLICANT,
                {
                    "applicant_id": str(person.id),
                    "name": f"{person.first_name} {person.last_name}",
                    "document_id": str(doc.id),
                    "matching_score": matching_score,
                },
            )
        )
        task.add_done_callback(
            lambda t: logger.error("Webhook failed: %s", t.exception())
            if t.exception()
            else None
        )

        return doc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.error("CV upload/parse failed for person_id=%s: %s", person_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CV processing failed",
        ) from exc


def list_applicants(
    db: Session,
    status_filter: PersonStatus | None,
    min_score: float | None,
    date_from: date | None,
    skip: int,
    limit: int,
) -> tuple[list[Person], int]:
    """Return paginated applicants with optional filters."""
    base_query = select(Person).where(Person.person_type == PersonType.applicant)

    if status_filter is not None:
        base_query = base_query.where(Person.status == status_filter)

    if date_from is not None:
        base_query = base_query.where(Person.created_at >= date_from)

    if min_score is not None:
        base_query = base_query.join(Person.documents).where(
            Document.matching_score >= min_score
        ).distinct()

    # Build count query independently to avoid DISTINCT subquery count issues
    count_base = select(func.count(Person.id.distinct())).where(
        Person.person_type == PersonType.applicant
    )
    if status_filter is not None:
        count_base = count_base.where(Person.status == status_filter)
    if date_from is not None:
        count_base = count_base.where(Person.created_at >= date_from)
    if min_score is not None:
        count_base = count_base.join(Person.documents).where(
            Document.matching_score >= min_score
        )
    total: int = db.execute(count_base).scalar_one()

    items = db.execute(
        base_query.order_by(Person.created_at.desc()).offset(skip).limit(limit)
    ).scalars().all()

    return list(items), total


def get_applicant(db: Session, applicant_id: UUID) -> Person:
    """Return a single applicant or raise 404."""
    person = db.execute(
        select(Person).where(
            Person.id == applicant_id,
            Person.person_type == PersonType.applicant,
        )
    ).scalar_one_or_none()

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Applicant {applicant_id} not found",
        )

    return person


def update_status(db: Session, applicant_id: UUID, data: ApplicantStatusUpdate) -> Person:
    """Update the status of an applicant."""
    person = get_applicant(db, applicant_id)

    try:
        person.status = data.status
        db.commit()
        db.refresh(person)
        logger.info("Applicant id=%s status changed to %s", applicant_id, data.status)
        return person
    except Exception as exc:
        db.rollback()
        logger.error("Status update failed for applicant id=%s: %s", applicant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status update failed",
        ) from exc


async def send_invite(db: Session, applicant_id: UUID) -> None:
    """Trigger n8n invite webhook for an applicant."""
    person = get_applicant(db, applicant_id)

    try:
        await webhook_service.trigger(
            settings.N8N_WEBHOOK_INVITE_APPLICANT,
            {
                "applicant_id": str(person.id),
                "name": f"{person.first_name} {person.last_name}",
            },
        )
        logger.info("Invite webhook sent for applicant id=%s", applicant_id)
    except Exception as exc:
        logger.error("Invite webhook failed for applicant id=%s: %s", applicant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invite could not be sent",
        ) from exc
