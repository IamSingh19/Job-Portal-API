from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    AccessTokenResponse,
)
from app.schemas.user import UserOut
from app.services import auth_handler

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register a new user",
    description="Register as a **job seeker** or **recruiter**. Recruiters must supply `company_name`.",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return auth_handler.register_user(request, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain JWT tokens",
    description="Returns an access token (30 min) and refresh token (7 days).",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return auth_handler.login_user(request, db)


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    return auth_handler.refresh_access_token(request.refresh_token, db)
