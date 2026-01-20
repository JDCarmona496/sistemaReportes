from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Reportes"
    API_V1_STR: str = "/api/v1"
    
    # ⚠️ CAMBIA ESTO por una cadena larga y aleatoria en producción
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # El token dura 1 hora

    class Config:
        env_file = ".env"

settings = Settings()