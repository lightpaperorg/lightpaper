import os

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://lightpaper:lightpaper_dev@localhost:5433/lightpaper",
    )
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    base_url: str = os.getenv("BASE_URL", "http://localhost:8001")
    cors_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,https://lightpaper.org",
        ).split(",")
    ]
    linkedin_client_id: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    linkedin_client_secret: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    gsc_service_account_key: str = os.getenv("GSC_SERVICE_ACCOUNT_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    stripe_api_key: str = os.getenv("STRIPE_API_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    ide_session_secret: str = os.getenv("IDE_SESSION_SECRET", "lightpaper-ide-dev-secret-change-me")


settings = Settings()
