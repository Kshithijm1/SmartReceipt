# backend/app/core/config.py
from pydantic import BaseSettings, AnyHttpUrl, PostgresDsn, validator
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartReceipt"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # DB
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Redis / Celery
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # AWS S3
    AWS_S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    # Hugging Face
    HF_MODEL_OCR: str = "microsoft/trocr-base-handwritten"
    HF_MODEL_TABLE: str = "google/tapas-base-finetuned-wtq"
    HF_MODEL_ZERO_SHOT: str = "facebook/bart-large-mnli"
    HF_MODEL_CLASSIFIER: str = "distilbert-base-uncased-finetuned-sst-2-english"

    # Monitoring & Logging
    SENTRY_DSN: Optional[str] = None
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def build_db_uri(cls, v, values):
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @validator("CELERY_BROKER_URL", pre=True)
    def build_celery_broker(cls, v, values):
        if v:
            return v
        host = values.get("REDIS_HOST")
        port = values.get("REDIS_PORT")
        return f"redis://{host}:{port}/0"

    @validator("CELERY_RESULT_BACKEND", pre=True)
    def build_celery_backend(cls, v, values):
        if v:
            return v
        host = values.get("REDIS_HOST")
        port = values.get("REDIS_PORT")
        return f"redis://{host}:{port}/1"


settings = Settings()
