from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Database
    database_url: str

    # JWT Configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: str = '["http://localhost:3000"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        return json.loads(self.cors_origins)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
