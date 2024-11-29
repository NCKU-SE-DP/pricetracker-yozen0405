from pydantic_settings import BaseSettings

class CrawlerConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "NEWS_"
        extra = "ignore"
    
    UDN_API_URL: str

crawler_config = CrawlerConfig()