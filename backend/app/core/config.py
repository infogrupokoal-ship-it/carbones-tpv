from typing import List, Optional
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = Field(default="Carbones y Pollos TPV Enterprise")
    APP_VERSION: str = Field(default="4.0.0-pro")
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="ultra_secret_key_pro_20x")
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = Field(default="sqlite:///./instance/tpv_data.sqlite")
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    INSTANCE_DIR: str = os.path.join(BASE_DIR, "instance")
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: List[str] = Field(default=["*"])

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
