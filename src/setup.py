# pylint: disable=invalid-name

"""
Setup configurations for project
"""

import sys
import os
from typing import Any, TypeVar
from datetime import datetime

from loguru import logger
from dotenv import dotenv_values

# Dynamic import for security
if "src" not in sys.path:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(base_dir)

from utils.security import SecurityHandler
from integrations.blob_storage import SupabaseStorage, BlobStorageFactory, StorageProviders


T = TypeVar("T")


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

        # Logger Config
        self.LOG_FILE_ACTIVE = self.get_env("LOG_FILE_ACTIVE", int, 0)

        # Supabase settings
        self.SUPABASE_URL = self.get_env("SUPABASE_URL", str)
        self.SUPABASE_KEY = self.get_env("SUPABASE_KEY", str)
        self.SUPABASE_STORAGE_NAME = self.get_env("SUPABASE_STORAGE_NAME", str)

        # Database
        self.DATABASE_SQLITE_PATH = self.get_env("DATABASE_PATH", str)\
            .replace("pymysql", "aiomysql")

    def get_env(
        self,
        key: str,
        ftype: T,
        default: Any = None,
        optional: bool = False
    ) -> T:
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

    def setup_loguru(self):
        """
        Setup loguru
        """

        # Setup log file if active
        if self.LOG_FILE_ACTIVE:
            logger.add(
                f"logs/run_{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.log",
                format=(
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                    "{level: <8} | "
                    "{name}:{function}:{line} | "
                    "{message} | "
                    "{extra}"
                ),
                level="INFO",
                rotation="10 MB",
                retention="1 days",
                compression="zip",
                enqueue=True,
            )

config = Config()
config.setup_loguru()
jwt_handler = SecurityHandler(config.JWT_SECRET_KEY)

# Blog configuration
store_supa_base = SupabaseStorage(
    supabase_key=config.SUPABASE_KEY,
    supabase_storage_name=config.SUPABASE_STORAGE_NAME,
    supabase_url=config.SUPABASE_URL,
)

storage_blob = BlobStorageFactory()
storage_blob.register(StorageProviders.SUPABASE, store_supa_base)

