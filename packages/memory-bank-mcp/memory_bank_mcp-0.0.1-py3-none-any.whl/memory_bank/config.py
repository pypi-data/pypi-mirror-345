"""
Configuration settings for Memory Bank application.
"""
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    db_path: Path = Field(default=Path("./memory_bank.db"))

    @validator('db_path', pre=True)
    def ensure_parent_dir_exists(cls, v):
        """Ensure the parent directory of the database file exists."""
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


# Create singleton settings instance
settings = Settings()