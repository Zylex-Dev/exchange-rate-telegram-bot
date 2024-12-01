from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGO_HOST: str = "db"
    MONGO_PORT: int = 27017
    MONGO_DB_NAME: str = "telegram_bot_db"
    MONGO_DB_URI: str

    TELEGRAM_BOT_TOKEN: str

    GOOGLE_FINANCE_URL: str = (
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies"
    )

    LOWER_THRESHOLD: float = 14.3
    SCHEDULER_DELAY: int = 30


settings = Settings()
