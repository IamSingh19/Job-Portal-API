from typing import List, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.bookmark import Bookmark
from app.models.job import Job
from app.models.user import User


def toggle_bookmark(job_id: int, user: User, db: Session) -> dict:
    """
    Add bookmark if not present, remove it if already bookmarked.
    Returns action taken: 'added' or 'removed'.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.job_id == job_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "removed", "job_id": job_id}

    bookmark = Bookmark(user_id=user.id, job_id=job_id)
    db.add(bookmark)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already bookmarked")

    return {"action": "added", "job_id": job_id}


def get_user_bookmarks(user: User, db: Session) -> Tuple[int, List[Bookmark]]:
    """Return all bookmarks for the authenticated user with embedded job data."""
    query = (
        db.query(Bookmark)
        .options(joinedload(Bookmark.job).joinedload(Job.recruiter))
        .filter(Bookmark.user_id == user.id)
        .order_by(Bookmark.created_at.desc())
    )
    total = query.count()
    return total, query.all()
