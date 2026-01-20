from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuración para encriptar passwords usando Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORRECCIÓN: Usamos Union[timedelta, None] para permitir nulos explícitamente
def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """Crea el Token JWT que enviaremos al usuario"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña plana con una encriptada"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña nueva"""
    return pwd_context.hash(password)