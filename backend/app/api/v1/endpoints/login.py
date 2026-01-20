from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Recibe usuario y contraseña. Si son correctos, devuelve un Token JWT.
    """
    # 1. Buscamos el usuario por email
    # Nota: OAuth2PasswordRequestForm usa 'username' para el campo principal (email en nuestro caso)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Verificamos contraseña
    if not user or not security.verify_password(form_data.password, user.hashed_password): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    # 3. Si todo está bien, creamos el token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }