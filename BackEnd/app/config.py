import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./adaptlearn.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-adaptlearn-hackathon-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    IMPORTANCE_THRESHOLD: float = float(os.getenv("IMPORTANCE_THRESHOLD", "0.7"))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
