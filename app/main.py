import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.session import Base, engine

# Import all models so SQLAlchemy registers them with Base.metadata
import app.models  # noqa: F401

from app.routes import auth, users, jobs, applications, bookmarks

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup (Alembic handles migrations in production)."""
    logger.info("Starting up Job Portal API …")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down Job Portal API …")


# ─── App Factory ──────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "## Job Portal REST API\n\n"
            "A production-ready job portal backend built with **FastAPI** + **MySQL**.\n\n"
            "### Features\n"
            "- 🔐 JWT Authentication (access + refresh tokens)\n"
            "- 👥 Role-based access (Job Seeker / Recruiter)\n"
            "- 💼 Full job CRUD with search & pagination\n"
            "- 📥 Job applications flow\n"
            "- 🔖 Job bookmarking\n\n"
            "### Auth\n"
            "Use the **Authorize** button (🔒) above and paste your `Bearer <access_token>`."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request timing middleware ─────────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}s"
        return response

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    # ── Routers ───────────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(jobs.router, prefix=api_prefix)
    app.include_router(applications.router, prefix=api_prefix)
    app.include_router(bookmarks.router, prefix=api_prefix)

    return app


app = create_app()
