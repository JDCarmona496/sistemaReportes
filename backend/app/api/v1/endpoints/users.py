from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

# Importamos Modelos (Base de Datos)
from app.models.user import User as UserModel 

# Importamos Schemas (Pydantic / Validación)
from app.schemas.user import User, UserCreate, UserUpdate

from app.api import deps
from app.core.security import get_password_hash

router = APIRouter()

# ==========================================
#  ENDPOINT PÚBLICO
# ==========================================

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    return current_user

# ==========================================
#  ENDPOINTS ADMIN
# ==========================================

# 1. LISTAR
@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

# 2. CREAR
@router.post("/", response_model=User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
):
    # type: ignore (Pylance se confunde con la comparación de Columnas)
    user = db.query(UserModel).filter(UserModel.email == user_in.email).first() 
    if user:
        raise HTTPException(
            status_code=400, detail="El usuario con este email ya existe."
        )

    db_obj = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
        is_active=user_in.is_active,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# 3. ACTUALIZAR
@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_data = user_in.model_dump(exclude_unset=True)

    if "password" in user_data and user_data["password"]:
        hashed = get_password_hash(user_data["password"])
        # Pylance cree que hashed_password es una Columna, no un string. Lo ignoramos.
        user.hashed_password = hashed # type: ignore 
        del user_data["password"]

    for field, value in user_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 4. ELIMINAR
@router.delete("/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser),
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first() # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Pylance se queja de comparar Columnas. Lo ignoramos porque en runtime son enteros.
    if user.id == current_user.id: # type: ignore
        raise HTTPException(
            status_code=400, detail="No puedes eliminar tu propio usuario activo."
        )

    db.delete(user)
    db.commit()
    return user