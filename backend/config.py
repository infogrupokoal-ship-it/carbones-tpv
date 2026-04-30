import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Configuración profesional centralizada para el ecosistema TPV Enterprise."""

    # APP METADATA
    APP_NAME: str = Field(default="Carbones y Pollos TPV Enterprise")
    APP_VERSION: str = Field(default="2.0.0-pro")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(default="tpv_ultra_secret_key_change_me_in_production")
    
    # DATABASE
    DATABASE_URL: str = Field(default="sqlite:///./tpv_data.sqlite")

    # OPERATIONAL SETTINGS
    LOG_LEVEL: str = Field(default="INFO")
    BRIDGE_PORT: int = Field(default=8022)
    CORS_ORIGINS: List[str] = Field(default=["*"])

    # EXTERNAL SERVICES
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    WAHA_URL: str = Field(default="http://localhost:3000")
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None)
    ADMIN_WHATSAPP: str = Field(default="34604864187@c.us")

    # BUSINESS LOGIC CONSTANTS
    CUBIERTOS_PRICE: float = 0.20
    VAT_REDUCED: float = 0.10
    VAT_STANDARD: float = 0.21

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
