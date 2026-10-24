from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings come from environment variables (or a .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Where we forward every customer message (our omnichannel API).
    omnichannel_webhook_url: str = "http://localhost:8000/webhooks/rahulcoolgram"
    # Shared secret sent in the X-RahulCoolGram-Key header, both directions.
    rahulcoolgram_api_key: str = "dev-secret"
    database_path: str = "rahulcoolgram.db"


settings = Settings()
