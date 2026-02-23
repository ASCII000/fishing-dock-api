"""
Module contains APP Fastapi
"""

from fastapi import FastAPI

from setup import config
from .dependencies.lifespan import lifespan
from .middlewares import setup_middlewares
from .controllers.users import setup_users_controllers
from .controllers.topics import setup_topics_controllers


app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

setup_middlewares(app)
setup_users_controllers(app)
setup_topics_controllers(app)
