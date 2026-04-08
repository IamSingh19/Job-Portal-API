from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.schemas.job import JobOut


class BookmarkToggleResponse(BaseModel):
    action: str      # "added" | "removed"
    job_id: int


class BookmarkOut(BaseModel):
    id: int
    user_id: int
    job_id: int
    created_at: datetime
    job: JobOut

    model_config = {"from_attributes": True}


class BookmarkListResponse(BaseModel):
    total: int
    items: List[BookmarkOut]
