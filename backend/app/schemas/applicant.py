from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.person import PersonStatus, PersonType


class ApplicantCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None


class ApplicantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    person_type: PersonType
    status: PersonStatus
    created_at: datetime
    matching_score: float | None = None


class ApplicantListResponse(BaseModel):
    items: list[ApplicantResponse]
    total: int
    page: int
    page_size: int


class ApplicantStatusUpdate(BaseModel):
    status: PersonStatus


class CVExtractedData(BaseModel):
    skills: list[str]
    roles: list[str]
    contact_info: dict[str, str]
