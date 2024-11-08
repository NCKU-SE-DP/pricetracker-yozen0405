from pydantic_settings import BaseSettings
import os

class AuthConfig(BaseSettings):
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        env_prefix = "JWT_"
        extra = "ignore"

    SECRET_KEY: str
    ALGORITHM: str
    AUTH_TOKEN_URL: str

auth_config = AuthConfig()