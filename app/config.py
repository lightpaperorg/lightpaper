import os
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://lightpaper:lightpaper_dev@localhost:5433/lightpaper",
    )
    firebase_project_id: str = os.getenv(
        "FIREBASE_PROJECT_ID", ""
    )
    base_url: str = os.getenv("BASE_URL", "http://localhost:8001")
    cors_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,https://lightpaper.org",
        ).split(",")
    ]


settings = Settings()
