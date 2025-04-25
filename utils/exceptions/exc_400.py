"""
Raises an HTTPException with status code 400 (Bad Request).

Note:
    Despite the function name suggesting a 500 Internal Server Error,
    it actually raises a 400 Bad Request error. Update the function name
    or status code to match the intended behavior.

Args:
    message (str): A descriptive error message.

Returns:
    HTTPException: FastAPI exception with status code 400.
"""

from fastapi import HTTPException, status


async def http_400_exc_bad_request(
        message: str = "Invalid request. Please verify the submitted data."
) -> Exception:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )
