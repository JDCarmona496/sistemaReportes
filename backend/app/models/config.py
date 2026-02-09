# type: ignore
from sqlalchemy import Column, String, Text
from app.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    category = Column(String(50), default="general")
