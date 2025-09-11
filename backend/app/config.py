"""Application configuration management."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql+asyncpg://legalease_user:legalease_password@localhost:5432/legalease_ai"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://legalease_user:legalease_password@localhost:5672/"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # AI/ML
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-1106-preview"
    openai_max_tokens: int = 4096
    
    # Vector Database
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "legalease-documents"
    
    # File Upload
    max_file_size_mb: int = 100
    allowed_file_types: str = "pdf,doc,docx,txt"
    upload_dir: str = "./uploads"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:80"
    
    # Development
    reload: bool = False
    workers: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()