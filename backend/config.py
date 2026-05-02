"""
Backend Configuration
Environment settings for the healthcare platform
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # App Settings
    APP_NAME = "AI Healthcare Assistant"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mongodb")  # mongodb or postgresql
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "healthcare_assistant")
    
    # PostgreSQL
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "healthcare_assistant")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq, openai, anthropic
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3-70b-8192")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Translation
    USE_GOOGLE_TRANSLATE = os.getenv("USE_GOOGLE_TRANSLATE", "false").lower() == "true"
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    
    # External APIs
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Email
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    
    # API Settings
    API_PREFIX = "/api/v1"
    API_TIMEOUT_SECONDS = 30
    MAX_REQUEST_SIZE_MB = 10
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
    
    # Security
    RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "100"))
    REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Chat Settings
    MAX_CHAT_MESSAGE_LENGTH = 5000
    MAX_CHAT_HISTORY_MESSAGES = 200
    CHAT_INACTIVITY_TIMEOUT_MINUTES = 60
    
    # Medical Settings
    MAX_EMERGENCY_RESPONSE_TIME_SECONDS = 5
    MEDICAL_DISCLAIMER = (
        "⚠️ MEDICAL DISCLAIMER: This is an AI-generated analysis and NOT a medical diagnosis. "
        "Please consult with a qualified healthcare professional for accurate diagnosis and treatment."
    )
    
    # Appointment
    MIN_APPOINTMENT_ADVANCE_HOURS = 1
    MAX_APPOINTMENT_ADVANCE_DAYS = 90
    APPOINTMENT_CONFIRMATION_EMAIL = True
    
    # Caching
    CACHE_ENABLED = True
    CACHE_TTL_SECONDS = 3600
    
    # Feature Flags
    ENABLE_VOICE_INPUT = os.getenv("ENABLE_VOICE_INPUT", "false").lower() == "true"
    ENABLE_VIDEO_CONSULTATION = os.getenv("ENABLE_VIDEO_CONSULTATION", "false").lower() == "true"
    ENABLE_PRESCRIPTION_GENERATION = os.getenv("ENABLE_PRESCRIPTION_GENERATION", "false").lower() == "true"
    ENABLE_MEDICAL_RECORDS = os.getenv("ENABLE_MEDICAL_RECORDS", "true").lower() == "true"
    ENABLE_TELEMEDICINE = os.getenv("ENABLE_TELEMEDICINE", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    REQUIRE_API_KEY = True


class TestingConfig(Config):
    """Testing configuration"""
    DATABASE_TYPE = "mongodb"
    MONGODB_DB_NAME = "healthcare_assistant_test"
    REDIS_ENABLED = False
    EMAIL_ENABLED = False
    LOG_LEVEL = "DEBUG"


def get_config() -> Config:
    """Get appropriate config based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


config = get_config()
