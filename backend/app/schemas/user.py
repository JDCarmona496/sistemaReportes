from typing import Optional
from pydantic import BaseModel, EmailStr


# 1. Base compartida (campos comunes)
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# 2. Para CREAR (Password obligatorio)
class UserCreate(UserBase):
    email: EmailStr | None = None 
    password: str
    full_name: str  | None = None


# 3. Para ACTUALIZAR (Password opcional) <--- ESTA ES LA QUE TE FALTA
class UserUpdate(UserBase):
    password: Optional[str] = None


# 4. Para LEER/RESPONDER (Sin password)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True
