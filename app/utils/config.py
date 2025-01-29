# app/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import validator

class Settings(BaseSettings):
    """
    Application settings and configuration.
    All settings are loaded from environment variables.
    """
    
    # MongoDB settings
    MONGODB_URL: str
    DATABASE_NAME: str
    
    # Google OAuth settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_REDIRECT_URI: str
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    
    # Server settings
    SERVER_HOST: str
    SERVER_PORT: int
    DEBUG_MODE: bool

    @validator('REFRESH_TOKEN_EXPIRE_MINUTES')
    def validate_refresh_token_expire_minutes(cls, v):
        """Validate refresh token expiration time"""
        if v <= 0:
            raise ValueError('REFRESH_TOKEN_EXPIRE_MINUTES must be positive')
        if v <= 1:
            raise ValueError('REFRESH_TOKEN_EXPIRE_MINUTES should be greater than 1 minute')
        return v

    class Config:
        """Pydantic configuration class"""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Returns the settings instance.
    Uses lru_cache to cache the settings and avoid loading .env file multiple times.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings() 