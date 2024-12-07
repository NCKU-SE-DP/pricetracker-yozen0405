from pydantic_settings import BaseSettings

class NewsConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "NEWS_"
        extra = "ignore"
    
    OPEN_AI_KEY: str

news_config = NewsConfig()