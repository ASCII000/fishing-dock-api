# pylint: disable=invalid-name

"""
Setup configurations for project
"""

from typing import Any

from loguru import logger
from dotenv import dotenv_values

from utils.security import SecurityHandler


class Config:
    """
    Project configurations
    """

    def __init__(self):
        self.config = dotenv_values(".env")

        # API Config
        self.API_PORT = self.get_env("API_PORT", int, 8000)
        self.API_HOST = self.get_env("API_HOST", str, "0.0.0.0")
        self.API_TITLE = self.get_env("API_TITLE", str, optional=True)
        self.API_DESCRIPTION = self.get_env("API_DESCRIPTION", str, optional=True)

        # JWT Config
        self.JWT_SECRET_KEY = self.get_env("JWT_SECRET_KEY", str)
        self.JWT_ACCESS_TOKEN_EXPIRES = self.get_env("JWT_EXPIRES_IN", int, 3600)
        self.JWT_REFRESH_TOKEN_EXPIRES = self.get_env("JWT_EXPIRES_IN", int, 86400)

        # Database
        self.DATABASE_SQLITE_PATH = self.get_env("DATABASE_SQLITE_PATH", str)

    def get_env(
        self,
        key: str,
        ftype: type,
        default: Any = None,
        optional: bool = False
    ):
        """
        Get environment variable

        Args:
            key (str): Environment variable key
            ftype (type): Environment variable type
            default (Any, optional): Default value. Defaults to None.
            optional (bool, optional): Default to False. If True, return default value if key not found
        """

        ctx_value = self.config.get(key, default)
        if optional and ctx_value is None:
            return default

        if not optional and ctx_value is None:
            raise ValueError(f"Variavel {key} nao encontrada")

        try:

            return ftype(ctx_value)

        except ValueError:

            logger.error(
                f"Tipo de variavel {key} deve ser {ftype.__name__} "
                f"e nao {type(ctx_value).__name__}"
            )

            raise


config = Config()
jwt_handler = SecurityHandler(config.JWT_SECRET_KEY)
