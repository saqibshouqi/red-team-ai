"""
Backend configuration settings
"""

import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings with validation"""

    def __init__(self):
        """Initialize and validate settings"""
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./red_team_ai.db")

        # Debug mode
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Application settings
        self.app_name: str = os.getenv("APP_NAME", "Red Team AI")
        self.version: str = os.getenv("APP_VERSION", "0.1.0")

        # CORS
        cors_origins_str = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins: List[str] = [
            origin.strip() for origin in cors_origins_str.split(",") if origin.strip()
        ]

        # API
        self.api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

        # Server
        self.host: str = os.getenv("HOST", "0.0.0.0")
        port_str = os.getenv("PORT", "8000")
        self.port: int = int(port_str)

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # Validate settings
        self._validate()

    def _validate(self):
        """Validate settings"""
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set")

        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}"
            )


settings = Settings()
