"""Auth request/response schemas.

Schemas validate data crossing the API boundary.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Input for login API.

    Input:
    - email: valid email string
    - password: raw password entered by user
    """

    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    """Input for registration API.

    TODO later:
    - split profile data to a dedicated profile schema
    - add favorite categories and travel preferences
    """

    email: EmailStr
    password: str = Field(min_length=6)


class AuthResponse(BaseModel):
    """Output for auth APIs.

    Output:
    - message: brief status summary
    - email: account email
    - access_token: optional JWT token for authenticated requests
    """

    message: str
    email: EmailStr
    access_token: str | None = None
