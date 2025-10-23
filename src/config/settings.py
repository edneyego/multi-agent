"""
Configurações da aplicação usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    default_model_provider: ModelProvider = ModelProvider.OPENAI
    default_model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # A2A Configuration
    a2a_server_host: str = "0.0.0.0"
    a2a_server_port: int = 8000
    a2a_agent_name: str = "multi-agent-system"
    a2a_agent_version: str = "1.0.0"
    
    # Weather API Configuration
    weather_api_base_url: str = "https://api.open-meteo.com/v1/forecast"
    
    # Application Configuration
    log_level: str = "INFO"
    debug: bool = False
    
    # MCP Configuration
    mcp_server_port: int = 3001
    mcp_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()