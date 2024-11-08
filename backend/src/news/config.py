from pydantic_settings import BaseSettings
import os

class NewsConfig(BaseSettings):
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        env_prefix = "NEWS_"
        extra = "ignore"
    
    UDN_API_URL: str

news_config = NewsConfig()