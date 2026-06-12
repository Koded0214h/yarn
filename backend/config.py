from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DATABASE_URL: str = 'postgresql://localhost/yarn'
    GEMINI_API_KEY: str = ''
    SERPAPI_KEY: str = ''
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_WHATSAPP_FROM: str = 'whatsapp:+14155238886'
    SENDGRID_API_KEY: str = ''
    FRONTEND_URL: str = 'http://localhost:5173'
    BASE_URL: str = 'http://localhost:8000'


@lru_cache
def get_settings() -> Settings:
    return Settings()
