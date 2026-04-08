from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.application import ApplicationStatus
from app.schemas.job import JobOut
from app.schemas.user import UserOut


class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = Field(None, max_length=5000, description="Optional cover letter (max 5000 chars)")


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    cover_letter: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Optionally embedded
    job: Optional[JobOut] = None
    applicant: Optional[UserOut] = None

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    total: int
    items: List[ApplicationOut]
