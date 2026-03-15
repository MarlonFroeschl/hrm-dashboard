import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.applicant import (
    ApplicantCreate,
    ApplicantListResponse,
    ApplicantResponse,
    ApplicantStatusUpdate,
)
from app.services import applicant_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Only PDF uploads are accepted for CV files
_ACCEPTED_CV_MIME = "application/pdf"


@router.post("/", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
async def create_applicant(
    data: ApplicantCreate,
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> ApplicantResponse:
    """Create a new applicant record."""
    try:
        person = await applicant_service.create_applicant(db, data)
        return ApplicantResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in create_applicant: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.post("/upload-cv", status_code=status.HTTP_202_ACCEPTED)
async def upload_cv(
    person_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> dict[str, str]:
    """Upload and parse a CV PDF for an existing applicant."""
    if file.content_type != _ACCEPTED_CV_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )

    try:
        doc = await applicant_service.upload_cv_and_parse(db, person_id, file)
        return {"document_id": str(doc.id), "status": "processing"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in upload_cv person_id=%s: %s", person_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get("/", response_model=ApplicantListResponse)
async def list_applicants(
    status_filter: PersonStatus | None = Query(None, alias="status"),
    min_score: float | None = Query(None, ge=0, le=100),
    date_from: date | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> ApplicantListResponse:
    """List applicants with optional filters and pagination."""
    try:
        skip = (page - 1) * page_size
        items, total = applicant_service.list_applicants(
            db,
            status_filter=status_filter,
            min_score=min_score,
            date_from=date_from,
            skip=skip,
            limit=page_size,
        )
        return ApplicantListResponse(
            items=[ApplicantResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in list_applicants: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get("/{applicant_id}", response_model=ApplicantResponse)
async def get_applicant(
    applicant_id: UUID,
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> ApplicantResponse:
    """Retrieve a single applicant by id."""
    try:
        person = applicant_service.get_applicant(db, applicant_id)
        return ApplicantResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in get_applicant id=%s: %s", applicant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.patch("/{applicant_id}/status", response_model=ApplicantResponse)
async def update_status(
    applicant_id: UUID,
    data: ApplicantStatusUpdate,
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> ApplicantResponse:
    """Update the status of an applicant."""
    try:
        person = applicant_service.update_status(db, applicant_id, data)
        return ApplicantResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in update_status id=%s: %s", applicant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.post("/{applicant_id}/invite", status_code=status.HTTP_202_ACCEPTED)
async def send_invite(
    applicant_id: UUID,
    db: Session = Depends(get_db),
    _current_user: str = Depends(get_current_user),
) -> dict[str, str]:
    """Trigger an invite webhook for an applicant."""
    try:
        await applicant_service.send_invite(db, applicant_id)
        return {"status": "invite_sent"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error in send_invite id=%s: %s", applicant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc
