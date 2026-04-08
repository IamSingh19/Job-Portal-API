from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.job import JobType
from app.schemas.job import JobCreate, JobUpdate, JobOut, JobListResponse
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobOut,
    status_code=201,
    summary="Create a new job listing",
    description="Available to **recruiters** only.",
)
def create_job(
    data: JobCreate,
    current_user: User = Depends(require_role([UserRole.recruiter])),
    db: Session = Depends(get_db),
):
    return job_service.create_job(data, current_user, db)


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all jobs",
    description="Search and paginate active job listings. No auth required.",
)
def list_jobs(
    search: Optional[str] = Query(None, description="Search by title or description"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
):
    total, jobs = job_service.list_jobs(db, search, location, job_type, page, page_size)
    return JobListResponse(total=total, page=page, page_size=page_size, items=jobs)


@router.get(
    "/{job_id}",
    response_model=JobOut,
    summary="Get a single job by ID",
)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_job_or_404(job_id, db)


@router.put(
    "/{job_id}",
    response_model=JobOut,
    summary="Update a job listing",
    description="Only the **recruiter who created** the job may update it.",
)
def update_job(
    job_id: int,
    data: JobUpdate,
    current_user: User = Depends(require_role([UserRole.recruiter])),
    db: Session = Depends(get_db),
):
    return job_service.update_job(job_id, data, current_user, db)


@router.delete(
    "/{job_id}",
    status_code=204,
    summary="Delete a job listing",
    description="Only the **recruiter who created** the job may delete it.",
)
def delete_job(
    job_id: int,
    current_user: User = Depends(require_role([UserRole.recruiter])),
    db: Session = Depends(get_db),
):
    job_service.delete_job(job_id, current_user, db)
