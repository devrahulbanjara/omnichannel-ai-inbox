from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Omnichannel AI Inbox API"
    environment: str = "dev"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
