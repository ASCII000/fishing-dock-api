"""
Module cotains APP Fastapi
"""

from fastapi import FastAPI

from setup import config
from .dependencies.lifespan import lifespan
from .dependencies.exception_handlers import setup_exception_handlers  # NOTE: Remove this module future use (setup_middlewares)
from .middlewares import setup_middlewares
from .controllers.users import setup_users_controllers


app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

setup_exception_handlers(app)
setup_users_controllers(app)
setup_middlewares(app)
