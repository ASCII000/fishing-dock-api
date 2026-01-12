"""
Global Exception Handlers
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import jwt

from domain.exceptions import SecurityError, NotFoundException, DuplicateException


def setup_exception_handlers(app: FastAPI):
    """
    Setup global exception handlers

    Args:
        app: FastAPI
    """

    @app.exception_handler(SecurityError)
    async def security_error_handler(request: Request, exc: SecurityError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.message}
        )

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message}
        )

    @app.exception_handler(DuplicateException)
    async def duplicate_handler(request: Request, exc: DuplicateException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message}
        )

    @app.exception_handler(jwt.InvalidTokenError)
    async def jwt_error_handler(request: Request, exc: jwt.InvalidTokenError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token inválido"}
        )

    @app.exception_handler(jwt.ExpiredSignatureError)
    async def jwt_expired_handler(request: Request, exc: jwt.ExpiredSignatureError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token expirado"}
        )
