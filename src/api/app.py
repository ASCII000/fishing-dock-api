"""
Module cotains APP Fastapi
"""

from fastapi import FastAPI

from setup import config
from .dependencies.lifespan import lifespan
from .controllers.users import register_router


app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(register_router, prefix="/users", tags=["Usuários"])
