# backend/app/schemas/config.py
from pydantic import BaseModel
from typing import Optional

class SettingBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = "general"

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: str # Solo permitimos actualizar el valor, no la clave

class Setting(SettingBase):
    class Config:
        from_attributes = True