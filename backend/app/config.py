import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"
    gemini_transcribe_model: str = "gemini-3.5-transcribe"

    # Hugging Face Configuration (for pyannote speaker diarization)
    hugging_face_token: str

    # Server Configuration
    backend_url: str = "http://localhost:8001"
    frontend_url: str = "http://localhost:5173"

    # File Upload Configuration
    max_file_size_mb: int = 500
    upload_directory: str = "./uploads"
    temp_directory: str = "./temp"

    # Processing Configuration
    processing_timeout: int = 3600

    # API Configuration
    api_title: str = "AI Meeting Insights API"
    api_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def __init__(self, **data):
        """Initialize settings and create required directories."""
        super().__init__(**data)

        # Create upload and temp directories if they don't exist
        Path(self.upload_directory).mkdir(parents=True, exist_ok=True)
        Path(self.temp_directory).mkdir(parents=True, exist_ok=True)


# Load settings
settings = Settings()
