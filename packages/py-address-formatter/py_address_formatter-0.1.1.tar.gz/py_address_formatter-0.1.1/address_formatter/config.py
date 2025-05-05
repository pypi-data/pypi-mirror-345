from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, Any, Optional
import os

class SwiftSettings(BaseSettings):
    """
    SWIFT message-specific configuration settings.
    
    This includes formatting rules, validation rules, and other
    SWIFT-specific settings.
    """
    # Default formatting rules for SWIFT messages
    default_max_line_length: int = Field(35, env="SWIFT_DEFAULT_MAX_LINE_LENGTH")
    default_max_lines: int = Field(4, env="SWIFT_DEFAULT_MAX_LINES")
    
    # Whether to strictly validate messages against SWIFT standards
    strict_validation: bool = Field(True, env="SWIFT_STRICT_VALIDATION")
    
    # Default character set allowed in SWIFT messages
    allowed_charset: str = Field("X", env="SWIFT_CHARSET")  # X, Y, or Z character sets
    
    class Config:
        env_prefix = "SWIFT_"
        case_sensitive = False

class APISettings(BaseSettings):
    """
    API-specific configuration settings.
    
    This includes settings for the API server, rate limiting,
    and security.
    """
    # Rate limiting
    rate_limit: int = Field(100, env="API_RATE_LIMIT")
    
    # Server settings
    host: str = Field("0.0.0.0", env="API_HOST")
    port: int = Field(8000, env="API_PORT")
    
    # Security settings
    enable_auth: bool = Field(False, env="API_ENABLE_AUTH")
    auth_secret: str = Field("", env="API_AUTH_SECRET")
    
    # Documentation settings
    enable_docs: bool = Field(True, env="API_ENABLE_DOCS")
    
    class Config:
        env_prefix = "API_"
        case_sensitive = False

class Settings(BaseSettings):
    """
    Configuration settings for the Address Formatter.
    Uses environment variables and .env file for configuration.
    """
    template_dir: str = Field("./data/templates", env="ADDRESS_TEMPLATE_DIR")
    cache_size: int = Field(1000, env="CACHE_SIZE")
    default_language: str = Field("en", env="DEFAULT_LANG")
    
    # Performance settings
    enable_async: bool = Field(False, env="ENABLE_ASYNC")
    enable_jit: bool = Field(False, env="ENABLE_JIT")
    thread_pool_size: int = Field(4, env="THREAD_POOL_SIZE")
    
    # API settings
    api: APISettings = APISettings()
    api_rate_limit: int = Field(100, env="API_RATE_LIMIT")  # Backward compatibility
    
    # SWIFT message-specific settings
    swift: SwiftSettings = SwiftSettings()
    
    # Supported message types
    supported_message_types: list = Field([
        "MT101", "MT102", "MT103", "MT110", 
        "MT202", "MT203", "MT205", "MT210",
        "MT400", "MT410", "MT700", "MT710", "MT720"
    ], env="SUPPORTED_MESSAGE_TYPES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_nested_delimiter = "__"

# Create a singleton instance of settings
settings = Settings() 