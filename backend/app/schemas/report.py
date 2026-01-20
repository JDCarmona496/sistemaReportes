from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# Definimos cómo se ve un parámetro de configuración
class ReportParamConfig(BaseModel):
    name: str       # Ej: "fecha_inicio" (debe coincidir con el SQL :fecha_inicio)
    type: str       # Ej: "date", "text", "number"
    label: str      # Ej: "Fecha de Inicio"
    required: bool = True

class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    sql_query: str
    requires_file: bool = False
    params_config: List[ReportParamConfig] = [] 

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