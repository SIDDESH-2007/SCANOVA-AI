import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://127.0.0.1:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "RADIOLOGY")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_key_radiology_12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    class Config:
        env_file = ".env"

settings = Settings()
