from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.bookmark import BookmarkListResponse, BookmarkToggleResponse
from app.services import bookmark_manager

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post(
    "/{job_id}",
    response_model=BookmarkToggleResponse,
    summary="Toggle bookmark on a job",
    description="**Job seekers** only. Adds the bookmark if not present; removes it if already bookmarked.",
)
def toggle_bookmark(
    job_id: int,
    current_user: User = Depends(require_role([UserRole.seeker])),
    db: Session = Depends(get_db),
):
    return bookmark_manager.toggle_bookmark(job_id, current_user, db)


@router.get(
    "",
    response_model=BookmarkListResponse,
    summary="List my bookmarked jobs",
    description="Returns all jobs bookmarked by the authenticated seeker.",
)
def list_bookmarks(
    current_user: User = Depends(require_role([UserRole.seeker])),
    db: Session = Depends(get_db),
):
    total, items = bookmark_manager.get_user_bookmarks(current_user, db)
    return BookmarkListResponse(total=total, items=items)
