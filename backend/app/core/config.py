from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "HRM Dashboard API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    # AI
    ANTHROPIC_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"

    # File uploads
    UPLOAD_DIR: str = "/app/uploads"
    MAX_CV_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # n8n Webhooks (extern – leer = deaktiviert)
    N8N_WEBHOOK_NEW_APPLICANT: str = ""
    N8N_WEBHOOK_INVITE_APPLICANT: str = ""
    N8N_WEBHOOK_ONBOARDING_START: str = ""
    N8N_WEBHOOK_OFFBOARDING_START: str = ""
    N8N_WEBHOOK_EMPLOYEE_UPDATED: str = ""


settings = Settings()  # type: ignore[call-arg]
