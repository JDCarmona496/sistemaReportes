from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PeriodicTaskBase(BaseModel):
    name: str                   # Ej: "Reporte Semanal Ventas"
    task: str                   # Ej: "app.worker.generar_reporte_pesado_task"
    args: Optional[List[Any]] = []      # Ej: [1, 5] (Argumentos posicionales)
    kwargs: Optional[Dict[str, Any]] = {} # Ej: {"formato": "PDF"}
    enabled: bool = True
    
    # Configuración de tiempo (CRON)
    # Ejemplo: min=0, hour=8 (Todos los días a las 8:00)
    crontab_minute: str = "*"
    crontab_hour: str = "*"
    crontab_day_of_week: str = "*"
    crontab_day_of_month: str = "*"
    crontab_month_of_year: str = "*"

class PeriodicTaskCreate(PeriodicTaskBase):
    pass

class PeriodicTaskUpdate(PeriodicTaskBase):
    pass

class PeriodicTask(PeriodicTaskBase):
    id: int
    last_run_at: Optional[Any] = None
    total_run_count: int = 0

    class Config:
        from_attributes = True