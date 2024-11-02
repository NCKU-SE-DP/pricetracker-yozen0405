from pydantic_settings import BaseSettings

class GlobalConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "GLOBAL_"
        extra = "ignore"

    SENTRY_DSN: str
    CORS_ALLOW_ORIGINS: str
    PROFILES_SAMPLE_RATE: float = 1.0
    TRACES_SAMPLE_RATE: float = 1.0
    FETCH_NEWS_INTERVAL_MINUTES: int = 100

global_config = GlobalConfig()