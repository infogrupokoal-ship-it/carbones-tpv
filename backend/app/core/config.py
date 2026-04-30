from typing import List, Optional
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Configuración Enterprise Centralizada v4.0."""

    # --- APP METADATA ---
    APP_NAME: str = Field(default="Carbones y Pollos TPV Ultra-Enterprise")
    APP_VERSION: str = Field(default="4.0.0-industrial")
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="tpv_ultra_secret_key_change_me_in_production")
    API_V1_STR: str = "/api/v1"

    # --- SECURITY ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    ALGORITHM: str = "HS256"

    # --- DATABASE ---
    # Si estamos en Render o similar, usaremos el DATABASE_URL proporcionado
    # De lo contrario, usamos SQLite en la carpeta instance
    DATABASE_URL: str = Field(default="sqlite:///./instance/tpv_data.sqlite")

    # --- PATHS ---
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOGS_DIR: str = os.path.join(BASE_DIR, "logs")
    INSTANCE_DIR: str = os.path.join(BASE_DIR, "instance")

    # --- OPERATIONAL ---
    LOG_LEVEL: str = Field(default="INFO")
    CORS_ORIGINS: List[str] = Field(default=["*"])

    # --- INTEGRATIONS ---
    WAHA_URL: str = Field(default="http://localhost:3000")
    ADMIN_WHATSAPP: str = Field(default="34604864187@c.us")
    STRIPE_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # --- BUSINESS CONSTANTS ---
    VAT_REDUCED: float = 0.10
    VAT_STANDARD: float = 0.21

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
