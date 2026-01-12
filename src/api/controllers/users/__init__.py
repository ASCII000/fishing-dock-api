"""
Setup user controllers
"""

from fastapi import FastAPI

from .routers.register_routers import router as register_router
from .routers.login_routers import router as login_router


def setup_users_controllers(app: FastAPI):
    """
    Setup user controllers

    Args:
        app: FastAPI
    """

    app.include_router(register_router, prefix="/users", tags=["Usuários"])
    app.include_router(login_router, prefix="/users/security", tags=["Usuários", "Segurança"])
