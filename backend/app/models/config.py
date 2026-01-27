# backend/app/models/config.py
from sqlalchemy import Column, String, Text
from app.database import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True, index=True) # Ej: "company_name"
    value = Column(Text, nullable=True)                     # Ej: "Laboratorio X"
    description = Column(String(255), nullable=True)        # Ej: "Nombre que sale en el PDF"
    category = Column(String(50), default="general")        # Ej: "general", "email", "sistema"