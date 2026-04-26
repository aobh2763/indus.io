from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "indus.io"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # ── Auth / JWT ───────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:mypassword@db:5432/indusdb"

    model_config = {
        "env_file": str(Path(__file__).resolve().parents[3] / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()