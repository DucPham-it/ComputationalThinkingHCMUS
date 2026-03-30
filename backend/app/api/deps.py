"""FastAPI dependency helpers.

Current state:
- returns a hard-coded demo user

TODO:
- replace with JWT-based authenticated user extraction
"""


def get_current_user() -> dict:
    """Return current user context.

    Output:
    - dict containing minimum user identity fields used by protected routes
    """
    return {"id": 1, "email": "demo@example.com"}
