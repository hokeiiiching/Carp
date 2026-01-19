"""Configuration classes for CARP application."""
import os
from typing import ClassVar


def get_database_url() -> str:
    """
    Get database URL with Vercel Postgres support.
    
    Vercel Postgres uses POSTGRES_URL with 'postgres://' prefix,
    but SQLAlchemy requires 'postgresql://' prefix.
    """
    # Check Vercel Postgres first
    url = os.environ.get('POSTGRES_URL')
    if url:
        # Vercel uses 'postgres://' but SQLAlchemy needs 'postgresql://'
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    
    # Fallback to DATABASE_URL or SQLite
    return os.environ.get('DATABASE_URL', 'sqlite:///carp.db')


class Config:
    """Base configuration with common settings."""
    
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = False
    SQLALCHEMY_DATABASE_URI: str = get_database_url()


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    
    DEBUG: ClassVar[bool] = True
    SQLALCHEMY_ECHO: ClassVar[bool] = True


class ProductionConfig(Config):
    """Production-specific configuration."""
    
    DEBUG: ClassVar[bool] = False
    
    def __init__(self) -> None:
        if self.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set in production environment")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
