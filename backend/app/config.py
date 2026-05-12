"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────
    APP_NAME: str = "AI Sales CRM"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # ── Database ─────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://crm:crm_password@localhost:5432/ai_crm"
    DATABASE_ECHO: bool = False

    # ── Redis ────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── n8n ──────────────────────────────────────────
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_API_KEY: Optional[str] = None
    N8N_INTERNAL_SECRET: str = "change-me-shared-secret"  # for n8n ↔ FastAPI auth

    # ── Auth (Clerk) ─────────────────────────────────
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_PUBLISHABLE_KEY: Optional[str] = None
    CLERK_JWT_ISSUER: Optional[str] = None

    # ── OpenAI ───────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None

    # ── Email (Resend) ───────────────────────────────
    RESEND_API_KEY: Optional[str] = None
    DEFAULT_FROM_EMAIL: str = "noreply@yourcrm.com"

    # ── SMS (Twilio) ─────────────────────────────────
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # ── Billing (Stripe) ─────────────────────────────
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # ── Google Calendar ──────────────────────────────
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None

    # ── CORS ─────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
