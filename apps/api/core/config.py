from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Omnichannel AI Inbox API"
    environment: str = "dev"
    log_level: str = "INFO"
    log_json: bool = False  # true in production: one JSON object per log line

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
