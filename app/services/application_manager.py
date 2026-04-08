from typing import List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate


def apply_to_job(
    job_id: int,
    data: ApplicationCreate,
    seeker: User,
    db: Session,
) -> Application:
    """Submit a job application. Raises 409 on duplicate application."""
    # Verify job exists and is active
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()  # noqa: E712
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or closed")

    application = Application(
        job_id=job_id,
        applicant_id=seeker.id,
        cover_letter=data.cover_letter,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        )

    db.refresh(application)
    return application


def get_my_applications(seeker: User, db: Session) -> Tuple[int, List[Application]]:
    """Return all applications submitted by the current seeker."""
    query = (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.recruiter))
        .filter(Application.applicant_id == seeker.id)
        .order_by(Application.created_at.desc())
    )
    total = query.count()
    return total, query.all()


def get_job_applicants(job_id: int, recruiter: User, db: Session) -> Tuple[int, List[Application]]:
    """Return all applicants for a job owned by the recruiter."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job listing")

    query = (
        db.query(Application)
        .options(joinedload(Application.applicant))
        .filter(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
    )
    total = query.count()
    return total, query.all()


def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    recruiter: User,
    db: Session,
) -> Application:
    """Allow the recruiter owning the job to update application status."""
    app = (
        db.query(Application)
        .options(joinedload(Application.job))
        .filter(Application.id == application_id)
        .first()
    )
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if app.job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job listing")

    app.status = data.status
    db.commit()
    db.refresh(app)
    return app
