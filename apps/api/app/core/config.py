from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Omnichannel AI Inbox API"
    environment: str = "dev"
    log_level: str = "INFO"
    log_json: bool = False  # one JSON object per log line
    database_url: str = "postgresql+asyncpg://inbox:inbox@localhost:5432/inbox"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
