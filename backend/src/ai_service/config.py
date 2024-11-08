from pydantic_settings import BaseSettings
import os

class AIConfig(BaseSettings):
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        env_prefix = "AI_"
        extra = "ignore"

    OPEN_AI_KEY: str
    OPEN_AI_MODEL: str

ai_config = AIConfig()