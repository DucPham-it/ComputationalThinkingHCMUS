from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.user_schema import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Authenticate user."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return AuthResponse(
        message="Login successful.",
        email=user.email,
        access_token=create_access_token(user.id, user.email),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Register a new user."""
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_email(payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )

    user = user_repo.create_user(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    return AuthResponse(
        message="Register successful.",
        email=user.email,
        access_token=create_access_token(user.id, user.email),
    )
