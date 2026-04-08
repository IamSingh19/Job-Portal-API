from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.job import ExperienceLevel, JobType
from app.schemas.user import UserOut


class JobCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=10000)
    location: str = Field(..., min_length=2, max_length=200)
    salary_min: Optional[Decimal] = Field(None, ge=0, description="Minimum salary (non-negative)")
    salary_max: Optional[Decimal] = Field(None, ge=0, description="Maximum salary (non-negative)")
    job_type: JobType = JobType.full_time
    experience_level: ExperienceLevel = ExperienceLevel.entry
    skills_required: Optional[str] = Field(None, max_length=500, description="Comma-separated skills e.g. 'Python,FastAPI,SQL'")

    @field_validator("salary_max")
    @classmethod
    def salary_range_valid(cls, v, info):
        if v is not None and info.data.get("salary_min") is not None:
            if v < info.data["salary_min"]:
                raise ValueError("salary_max must be >= salary_min")
        return v


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    skills_required: Optional[str] = None
    is_active: Optional[bool] = None


class JobOut(BaseModel):
    id: int
    title: str
    description: str
    location: str
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    job_type: JobType
    experience_level: ExperienceLevel
    skills_required: Optional[str] = None
    is_active: bool
    recruiter_id: int
    recruiter: Optional[UserOut] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[JobOut]
