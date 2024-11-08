from pydantic_settings import BaseSettings

class PricingConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "PRICING_"
        extra = "ignore"

    NECESSITIES_PRICE_API_URL: str 
    
pricing_config = PricingConfig()