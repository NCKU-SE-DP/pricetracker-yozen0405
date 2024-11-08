from pydantic_settings import BaseSettings
import os

class PricingConfig(BaseSettings):
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        env_prefix = "PRICING_"
        extra = "ignore"

    NECESSITIES_PRICE_API_URL: str 
    
pricing_config = PricingConfig()