from pydantic import BaseModel, EmailStr

# Propiedades compartidas
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    full_name: str | None = None

# Propiedades para crear un usuario (lo usaremos luego)
class UserCreate(UserBase):
    password: str

# Propiedades para devolver al cliente (¡SIN PASSWORD!)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Antes se llamaba orm_mode