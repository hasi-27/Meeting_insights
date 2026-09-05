from fastapi import HTTPException
from typing import Any


def handle_error(error: Exception, context: str) -> HTTPException:
    """
    Convert exceptions to HTTP responses.

    Args:
        error: The exception that occurred
        context: Description of what was being done

    Returns:
        HTTPException with appropriate status code
    """
    error_msg = str(error)

    # File format errors
    if "Unsupported file format" in error_msg:
        return HTTPException(status_code=400, detail=error_msg)

    # File size errors
    if "exceeds maximum size" in error_msg:
        return HTTPException(status_code=413, detail=error_msg)

    # Not found errors
    if "not found" in error_msg:
        return HTTPException(status_code=404, detail=error_msg)

    # Validation errors
    if "ValueError" in str(type(error)):
        return HTTPException(status_code=400, detail=str(error))

    # Default server error
    return HTTPException(
        status_code=500, detail=f"{context}: {error_msg}"
    )
