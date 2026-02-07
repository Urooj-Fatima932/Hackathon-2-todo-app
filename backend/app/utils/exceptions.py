from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handler for uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
