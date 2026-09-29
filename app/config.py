from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    JWT_SECRET: str
    JWT_ALGORITHM: str

    PRIVATE_KEY_PATH: Path = BASE_DIR / "keys" / "private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "keys" / "public.pem"

    
    POSTGRES_CONNECT: str

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

