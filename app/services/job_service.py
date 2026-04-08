from typing import Optional, Tuple, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate


def create_job(data: JobCreate, recruiter: User, db: Session) -> Job:
    """Create a new job listing owned by the recruiter."""
    job = Job(
        **data.model_dump(),
        recruiter_id=recruiter.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_or_404(job_id: int, db: Session) -> Job:
    """Fetch a job by ID or raise 404."""
    job = (
        db.query(Job)
        .options(joinedload(Job.recruiter))
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


def list_jobs(
    db: Session,
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[int, List[Job]]:
    """
    Return paginated, optionally filtered/searched list of active jobs.
    search: matches against title or description
    location: case-insensitive substring match
    """
    query = (
        db.query(Job)
        .options(joinedload(Job.recruiter))
        .filter(Job.is_active == True)  # noqa: E712
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Job.title.ilike(pattern), Job.description.ilike(pattern))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter(Job.job_type == job_type)

    total = query.count()
    jobs = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, jobs


def update_job(job_id: int, data: JobUpdate, recruiter: User, db: Session) -> Job:
    """Update a job. Only the owning recruiter may update."""
    job = get_job_or_404(job_id, db)
    if job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job listing")

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


def delete_job(job_id: int, recruiter: User, db: Session) -> None:
    """Delete a job. Only the owning recruiter may delete."""
    job = get_job_or_404(job_id, db)
    if job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job listing")

    db.delete(job)
    db.commit()
