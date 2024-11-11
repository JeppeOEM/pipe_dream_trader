
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()

