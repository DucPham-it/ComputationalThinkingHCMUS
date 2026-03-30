from fastapi import APIRouter

from app.core.security import hash_password
from app.schemas.user_schema import AuthResponse, LoginRequest, RegisterRequest

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    """Authenticate user.

    Input:
    - email and password from login form

    Output:
    - auth response with message and optional access token

    TODO:
    - query user by email
    - verify password hash
    - issue JWT token
    """
    return AuthResponse(message="Login endpoint placeholder", email=payload.email, access_token=None)


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest) -> AuthResponse:
    """Register a new user.

    TODO:
    - validate email uniqueness
    - hash password securely
    - save user to SQL Server
    - optionally return JWT token
    """
    _password_hash = hash_password(payload.password)
    return AuthResponse(message="Register endpoint placeholder", email=payload.email, access_token=None)
