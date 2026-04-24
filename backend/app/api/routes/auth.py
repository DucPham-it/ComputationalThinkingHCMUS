from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.repositories.admin_repo import AdminRepository
from app.repositories.user_repo import UserRepository
from app.schemas.user_schema import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)

router = APIRouter()


def _auth_response(
    message: str,
    user,
    *,
    db: Session,
    access_token: str | None = None,
) -> AuthResponse:
    is_admin = AdminRepository(db).is_approved_admin(user.id)
    return AuthResponse(
        message=message,
        user=UserResponse(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            birth_date=user.birth_date,
            gender=user.gender,
            address=user.address,
            avatar_url=user.avatar_url,
            is_admin=is_admin,
        ),
        access_token=access_token,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Authenticate user."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_identifier(payload.identifier)
    if user is None or user.is_virtual or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )

    return _auth_response(
        message="Login successful.",
        user=user,
        db=db,
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

    existing_user_name = user_repo.get_by_user_name(payload.user_name)
    if existing_user_name is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = user_repo.create_user(
        email=payload.email,
        password_hash=hash_password(payload.password),
        user_name=payload.user_name,
    )

    return _auth_response(
        message="Register successful.",
        user=user,
        db=db,
        access_token=create_access_token(user.id, user.email),
    )


@router.put("/profile", response_model=AuthResponse)
def update_profile(
    payload: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthResponse:
    """Complete or update the current user's profile."""
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_id(current_user["id"])
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user = user_repo.update_profile(
        user_id=current_user["id"],
        first_name=payload.first_name,
        last_name=payload.last_name,
        birth_date=payload.birth_date,
        gender=payload.gender,
        address=payload.address,
    )
    return _auth_response(
        message="Profile updated successfully.",
        user=user,
        db=db,
    )
