from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "lumiere"
    valkey_url: str = "redis://localhost:6379"
    admin_token: str = "dev-token-change-me"
    whatsapp_number: str = "+1XXXXXXXXXX"
    cache_ttl_seconds: int = 600
    images_base_url: str = "http://localhost:8000/static/images"

    class Config:
        env_file = ".env"

settings = Settings()
