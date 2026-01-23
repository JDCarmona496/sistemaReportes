from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Reportes"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad JWT
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 

    # Base de Datos Local
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/reportes_db"

    # --- NUEVA VARIABLE (Corrección del error 1 y 2) ---
    # Lista de orígenes permitidos para CORS (Frontend)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000", 
        "http://127.0.0.1:8000"
    ]

    # Datos LIS
    LIS_HOST: str = "localhost"
    LIS_DB: str = "WINSISLAB"
    LIS_USER: str = "postgres"
    LIS_PASSWORD: str = ""
    LIS_PORT: str = "5432"

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()