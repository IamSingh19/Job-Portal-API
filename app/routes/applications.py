from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationListResponse,
    ApplicationStatusUpdate,
)
from app.services import application_manager

router = APIRouter(prefix="/applications", tags=["Applications"])


# ── Static routes MUST come before dynamic /{job_id} routes ──────────────────

@router.get(
    "/me",
    response_model=ApplicationListResponse,
    summary="View my applications",
    description="Returns all jobs the authenticated **job seeker** has applied to.",
)
def my_applications(
    current_user: User = Depends(require_role([UserRole.seeker])),
    db: Session = Depends(get_db),
):
    total, items = application_manager.get_my_applications(current_user, db)
    return ApplicationListResponse(total=total, items=items)


@router.get(
    "/job/{job_id}",
    response_model=ApplicationListResponse,
    summary="View applicants for a job",
    description="**Recruiters** only. Returns applicants for a job they own.",
)
def job_applicants(
    job_id: int,
    current_user: User = Depends(require_role([UserRole.recruiter])),
    db: Session = Depends(get_db),
):
    total, items = application_manager.get_job_applicants(job_id, current_user, db)
    return ApplicationListResponse(total=total, items=items)


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationOut,
    summary="Update application status",
    description="**Recruiters** can update status: pending → reviewed → shortlisted → accepted/rejected.",
)
def update_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(require_role([UserRole.recruiter])),
    db: Session = Depends(get_db),
):
    return application_manager.update_application_status(application_id, data, current_user, db)


# ── Dynamic routes come last ──────────────────────────────────────────────────

@router.post(
    "/{job_id}",
    response_model=ApplicationOut,
    status_code=201,
    summary="Apply to a job",
    description="**Job seekers** only. Raises 409 on duplicate application.",
)
def apply_to_job(
    job_id: int,
    data: ApplicationCreate,
    current_user: User = Depends(require_role([UserRole.seeker])),
    db: Session = Depends(get_db),
):
    return application_manager.apply_to_job(job_id, data, current_user, db)
