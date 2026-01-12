"""
Main module project
"""

import uvicorn
from api import app
from setup import config


if __name__ == "__main__":

    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )
