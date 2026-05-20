from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/pricewatch"
    secret_key: str = "dev-secret-key"
    scraper_interval_hours: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
