from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_db_url: str = ""
    anthropic_api_key: str = ""
    dataforseo_login: str = ""
    dataforseo_password: str = ""
    ahrefs_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]
    api_secret_key: str = "change-me"


settings = Settings()
