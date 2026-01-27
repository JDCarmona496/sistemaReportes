from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Importamos el MODELO DE BASE DE DATOS (User)
from app.models.user import User 
from app.core import security
from app.core.config import settings
from app.database import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Buscamos en la BD usando el Modelo User
    user = db.query(User).filter(User.id == token_data).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    # Verificamos si es superusuario usando el atributo del modelo
    if not current_user.is_superuser: # type: ignore
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user