from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore
from pydantic import BaseModel

from app.api import deps
from app.database import get_db
from app.models.config import SystemSetting
from app.schemas import config as config_schema

router = APIRouter()


# Schema especial para recibir actualizaciones en lote
class SettingsBulkUpdate(BaseModel):
    settings: Dict[str, str]  # {"company_name": "Nuevo Nombre", "otro": "valor"}


@router.get("/", response_model=List[config_schema.Setting])
def read_settings(
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_user),
):
    return db.query(SystemSetting).all()


@router.put("/", status_code=200)
def update_settings(
    update_data: SettingsBulkUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_active_superuser),  # SOLO ADMIN
):
    """
    Recibe un JSON tipo {"clave": "valor", "clave2": "valor2"} y actualiza todo.
    """
    count = 0
    for key, value in update_data.settings.items():
        # type: ignore (Pylance se queja de la comparación de columnas y llamadas opcionales)
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()  # type: ignore
        if setting:
            # CORRECCIÓN: Agregamos type: ignore para evitar el error de asignación de columna
            setting.value = value  # type: ignore
            count += 1

    db.commit()
    return {"message": f"{count} configuraciones actualizadas correctamente."}
