from pydantic_settings import BaseSettings
from pydantic import Field

class PricingConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "PRICING_"
        extra = "ignore"

    necessities_price_api_url: str 
    
pricing_settings = PricingConfig()

