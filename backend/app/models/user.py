"""Internal user model.

Represents a user record retrieved from the database.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    """User entity.

    Fields:
    - id: internal user identifier
    - user_name: username used for login
    - email: account email used for login
    - password_hash: hashed password stored in database
    - first_name: user's given name
    - last_name: user's family name
    - birth_date: user's date of birth
    - gender: user's gender
    - address: user's address
    """

    id: int
    user_name: str
    email: str
    password_hash: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    address: str | None = None
