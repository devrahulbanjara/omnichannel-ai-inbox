from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Omnichannel AI Inbox API"
    environment: str = "dev"
    log_level: str = "INFO"
    log_json: bool = False  # one JSON object per log line
    database_url: str = "postgresql+asyncpg://inbox:inbox@localhost:5432/inbox"
    cors_origins: list[str] = ["http://localhost:3000"]  # browser origins allowed to call the API
    rahulcoolgram_url: str = "http://localhost:8100"
    rahulcoolgram_api_key: str = "dev-secret"  # shared key, sent as X-RahulCoolGram-Key both ways

    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_api_key: SecretStr = SecretStr("")
    groq_model: str = ""
    groq_timeout_seconds: float = 20  # per attempt
    groq_max_retries: int = 2  # after the first attempt

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
