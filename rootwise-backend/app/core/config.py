
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ROOTWISE"
    APP_ENV: str = "development"

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""

    ALLOW_GUEST_DEMO: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
