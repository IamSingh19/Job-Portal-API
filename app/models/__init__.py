# models package — import all models here so Alembic can discover them
from app.models.user import User, UserRole  # noqa: F401
from app.models.job import Job, JobType, ExperienceLevel  # noqa: F401
from app.models.application import Application, ApplicationStatus  # noqa: F401
from app.models.bookmark import Bookmark  # noqa: F401
