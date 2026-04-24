"""Auth request/response schemas.

Schemas validate data crossing the API boundary.
"""

from datetime import date

from pydantic import AliasChoices, BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Input for login API.

    Input:
    - identifier: username or email used for login
    - password: raw password entered by user
    """

    identifier: str = Field(
        min_length=1,
        validation_alias=AliasChoices("identifier", "email", "user_name"),
    )
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    """Input for registration API.

    TODO later:
    - split profile data to a dedicated profile schema
    - add favorite categories and travel preferences
    """

    user_name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class UpdateProfileRequest(BaseModel):
    """Input for profile completion/update after registration."""

    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    birth_date: date
    gender: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = Field(default=None, min_length=1, max_length=500)


class UserResponse(BaseModel):
    """Serialized user profile returned by auth APIs."""

    id: int
    user_name: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    is_admin: bool = False


class AuthResponse(BaseModel):
    """Output for auth APIs."""

    message: str
    user: UserResponse
    access_token: str | None = None
