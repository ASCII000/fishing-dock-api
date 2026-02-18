"""
Mock config for testing
"""


class MockConfig:
    """
    Mock configuration for testing without .env file
    """

    def __init__(self):
        # API Config
        self.API_PORT = 8000
        self.API_HOST = "0.0.0.0"
        self.API_TITLE = "Test API"
        self.API_DESCRIPTION = "Test API Description"

        # JWT Config - use a proper length key for tests
        self.JWT_SECRET_KEY = "test-secret-key-with-minimum-32-bytes!"
        self.JWT_ACCESS_TOKEN_EXPIRES = 3600
        self.JWT_REFRESH_TOKEN_EXPIRES = 86400

        # Logger Config
        self.LOG_FILE_ACTIVE = 0

        # Supabase settings (fake values for testing)
        self.SUPABASE_URL = "https://mock-supabase.example.com"
        self.SUPABASE_KEY = "mock-supabase-key"
        self.SUPABASE_STORAGE_NAME = "mock-storage"

        # Database (in-memory SQLite for tests)
        self.DATABASE_SQLITE_PATH = "sqlite+aiosqlite:///:memory:"

    def setup_loguru(self):
        """
        No-op for testing
        """
        pass
