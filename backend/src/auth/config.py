from pydantic_settings import BaseSettings

class AuthConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "JWT_"
        extra = "ignore"

    SECRET_KEY: str
    ALGORITHM: str

auth_settings = AuthConfig()