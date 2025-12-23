"""
=============================================================================
Configuration Settings for SmartCareer AI
=============================================================================

This file manages all application settings using Pydantic.
Settings are automatically loaded from environment variables or .env file.

USAGE:
    from app.config import settings
    
    # Access any setting
    api_key = settings.OPENAI_API_KEY
    model = settings.OPENAI_MODEL

HOW IT WORKS:
    1. Pydantic looks for a .env file in the project root
    2. Each setting maps to an environment variable
    3. If not found, the default value is used
    4. Type validation is automatic
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import List, Union
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings have default values for easy development,
    but you should set proper values in production.
    """
    
    # =========================================================================
    # 🔑 OPENAI API CONFIGURATION
    # =========================================================================
    
    # Your OpenAI API key (required for AI features)
    # Get it from: https://platform.openai.com/api-keys
    OPENAI_API_KEY: str = ""
    
    # Which GPT model to use
    # Options: "gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Maximum tokens for AI responses
    # Higher = longer responses but more cost
    # Resume generation typically needs 1500-2000 tokens
    OPENAI_MAX_TOKENS: int = 2000
    
    # Temperature controls randomness (0.0 to 1.0)
    # Lower = more consistent, Higher = more creative
    OPENAI_TEMPERATURE: float = 0.7
    
    # Number of retry attempts if API call fails
    OPENAI_MAX_RETRIES: int = 3
    
    # Timeout for API calls in seconds
    OPENAI_TIMEOUT: int = 60
    
    # =========================================================================
    # 🌟 GOOGLE GEMINI API CONFIGURATION (BEPUL!)
    # =========================================================================
    
    # Gemini API kaliti - BEPUL!
    # Olish: https://ai.google.dev/
    GEMINI_API_KEY: str = ""
    
    # Gemini model tanlash
    # "gemini-1.5-flash" - Tez va bepul
    # "gemini-1.5-pro" - Kuchliroq
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # AI provider tanlash: "gemini" yoki "openai"
    AI_PROVIDER: str = "gemini"
    
    # =========================================================================
    # 🗄️ DATABASE CONFIGURATION
    # =========================================================================
    
    # Database connection string
    # Development: SQLite
    # Production: postgresql://user:password@host:port/database
    DATABASE_URL: str = "sqlite:///./smartcareer.db"
    
    # =========================================================================
    # 🔐 JWT AUTHENTICATION
    # =========================================================================
    
    # Secret key for signing JWT tokens
    # IMPORTANT: Generate a unique random key for production!
    # Generate with: openssl rand -hex 32
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # JWT algorithm (HS256 is standard and secure)
    ALGORITHM: str = "HS256"
    
    # Access token lifetime in minutes (short for security)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Refresh token lifetime in days (longer, for convenience)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # =========================================================================
    # 🌐 APPLICATION SETTINGS
    # =========================================================================
    
    # Application name (shown in API docs and responses)
    APP_NAME: str = "SmartCareer AI"
    
    # Version number
    APP_VERSION: str = "1.0.0"
    
    # Debug mode
    # True: Shows detailed errors, enables /docs endpoint
    # False: Hides errors, disables /docs (use in production)
    DEBUG: bool = True
    
    # =========================================================================
    # 📁 FILE UPLOAD SETTINGS
    # =========================================================================
    
    # Directory for storing uploaded files
    UPLOAD_DIR: str = "uploads"
    
    # Maximum file size in bytes (default: 10MB)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    # Allowed file extensions for resume uploads
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc", ".txt"]
    
    # =========================================================================
    # 📧 EMAIL SETTINGS (SMTP)
    # =========================================================================
    
    # SMTP server settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@smartcareer.uz"
    SMTP_FROM_NAME: str = "SmartCareer AI"
    SMTP_USE_TLS: bool = True
    
    # SendGrid (optional - for production)
    SENDGRID_API_KEY: str = ""
    
    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Support email
    SUPPORT_EMAIL: str = "support@smartcareer.uz"
    
    # =========================================================================
    # 🔐 OAUTH2 SETTINGS (Google, LinkedIn)
    # =========================================================================
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback/google"
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback/linkedin"
    
    # OAuth enabled
    OAUTH_ENABLED: bool = False
    
    # =========================================================================
    # 🔗 CORS SETTINGS
    # =========================================================================
    
    # Allowed origins for CORS (frontend URLs)
    # Add your frontend URL for production
    # Can be comma-separated string or JSON list
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS_ORIGINS as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS
    
    # =========================================================================
    # PYDANTIC CONFIGURATION
    # =========================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using @lru_cache ensures settings are only loaded once,
    which improves performance.
    
    Returns:
        Settings instance with all configuration values
    """
    return Settings()


# Create a global settings instance for easy importing
# Usage: from app.config import settings
settings = get_settings()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_openai_config() -> dict:
    """
    Validate OpenAI configuration and return status.
    
    Use this to check if the AI service is properly configured
    before attempting to use it.
    
    Returns:
        Dictionary with validation results
        
    Example:
        status = validate_openai_config()
        if not status["valid"]:
            print(f"Error: {status['message']}")
    """
    if not settings.OPENAI_API_KEY:
        return {
            "valid": False,
            "message": "OPENAI_API_KEY is not set",
            "help": "Get your API key from https://platform.openai.com/api-keys"
        }
    
    if not settings.OPENAI_API_KEY.startswith("sk-"):
        return {
            "valid": False,
            "message": "OPENAI_API_KEY appears to be invalid (should start with 'sk-')",
            "help": "Check that you copied the full API key"
        }
    
    valid_models = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
    if settings.OPENAI_MODEL not in valid_models:
        return {
            "valid": False,
            "message": f"OPENAI_MODEL '{settings.OPENAI_MODEL}' is not recognized",
            "help": f"Valid models: {', '.join(valid_models)}"
        }
    
    return {
        "valid": True,
        "message": "OpenAI configuration is valid",
        "model": settings.OPENAI_MODEL,
        "max_tokens": settings.OPENAI_MAX_TOKENS
    }


def print_config_summary():
    """
    Print a summary of current configuration.
    
    Useful for debugging and verifying settings on startup.
    Masks sensitive values like API keys.
    """
    def mask_key(key: str) -> str:
        """Mask API key, showing only first and last 4 characters."""
        if not key or len(key) < 10:
            return "NOT SET"
        return f"{key[:4]}...{key[-4:]}"
    
    print("\n" + "=" * 60)
    print("📋 SMARTCAREER AI - CONFIGURATION SUMMARY")
    print("=" * 60)
    
    print("\n🔑 OpenAI Configuration:")
    print(f"   API Key:     {mask_key(settings.OPENAI_API_KEY)}")
    print(f"   Model:       {settings.OPENAI_MODEL}")
    print(f"   Max Tokens:  {settings.OPENAI_MAX_TOKENS}")
    print(f"   Temperature: {settings.OPENAI_TEMPERATURE}")
    
    print("\n🗄️ Database:")
    # Mask password in database URL
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        parts = db_url.split("@")
        masked_url = parts[0].rsplit(":", 1)[0] + ":****@" + parts[1]
    else:
        masked_url = db_url
    print(f"   URL: {masked_url}")
    
    print("\n🌐 Application:")
    print(f"   Name:    {settings.APP_NAME}")
    print(f"   Version: {settings.APP_VERSION}")
    print(f"   Debug:   {settings.DEBUG}")
    
    print("\n🔗 CORS Origins:")
    for origin in settings.cors_origins_list:
        print(f"   - {origin}")
    
    print("\n" + "=" * 60 + "\n")


# =============================================================================
# STARTUP VALIDATION
# =============================================================================

# Uncomment to print config summary on import (useful for debugging)
# print_config_summary()
