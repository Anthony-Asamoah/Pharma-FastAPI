"""
Raises an HTTPException with status code 409 (Conflict).

Typically used when a request could not be completed due to a conflict
with the current state of the target resource (e.g., duplicate entries,
version conflicts).

Args:
    message (str): A descriptive error message explaining the conflict.

Returns:
    HTTPException: FastAPI exception with status code 409.
"""

from fastapi import HTTPException, status


async def http_409_exc_conflict(
        message: str
) -> Exception:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )
