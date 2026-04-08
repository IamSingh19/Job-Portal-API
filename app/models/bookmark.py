from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # A user can only bookmark a job once
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_bookmark"),
    )

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    job = relationship("Job", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark id={self.id} user_id={self.user_id} job_id={self.job_id}>"
