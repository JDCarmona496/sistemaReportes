from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.report import Report
from app.schemas import report as report_schema

router = APIRouter()

# 1. Listar todos los reportes (Para llenar tu menú lateral)
@router.get("/", response_model=List[report_schema.Report])
def read_reports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user) # Requiere Login
):
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

# 2. Crear un nuevo reporte (Para guardar tu Query)
@router.post("/", response_model=report_schema.Report)
def create_report(
    *,
    db: Session = Depends(get_db),
    report_in: report_schema.ReportCreate,
    current_user = Depends(deps.get_current_user)
):
    # Convertimos el modelo Pydantic a diccionario, pero params_config requiere cuidado
    # Pydantic .dict() o .model_dump() maneja la conversión a JSON automáticamente
    report_data = report_in.dict()
    
    db_report = Report(**report_data)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

# 3. Obtener detalle de un reporte (Para mostrar el módulo de configuración)
@router.get("/{report_id}", response_model=report_schema.Report)
def read_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    current_user = Depends(deps.get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report