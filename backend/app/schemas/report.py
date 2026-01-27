from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


# Definimos cómo se ve un parámetro de configuración
class ReportParamConfig(BaseModel):
    name: str  # Ej: "fecha_inicio" (debe coincidir con el SQL :fecha_inicio)
    type: str  # Ej: "date", "text", "number"
    label: str  # Ej: "Fecha de Inicio"
    required: bool = True


class ReportBase(BaseModel):
    title: str
    sql_query: str
    description: Optional[str] = None
    params_config: Optional[List[Dict[str, Any]]] = []
    layout: Optional[str] = "tabla"


class ReportCreate(ReportBase):
    pass


class ReportUpdate(ReportBase):
    pass


class Report(ReportBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
