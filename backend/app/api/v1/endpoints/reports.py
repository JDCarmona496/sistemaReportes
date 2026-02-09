from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore
from pydantic import BaseModel

from app.api import deps
from app.database import get_db
from app.models.report import Report
from app.schemas import report as report_schema

# --- IMPORTACIONES DE CELERY ---
from app.worker import generar_reporte_pesado_task
from app.core.celery_app import celery_app

router = APIRouter()


# --- MODELO PARA EL BODY DEL REQUEST DE GENERACIÓN ---
class ReporteRequest(BaseModel):
    reporte_id: int
    params: Dict[str, Any]
    formato: str = "PDF"


# =========================================================
# 1. RUTAS DE USO GENERAL (Operadores y Admins)
# =========================================================


# --- GENERAR REPORTE (Cualquier usuario logueado) ---
@router.post("/generar-background")
def iniciar_generacion_reporte(
    request: ReporteRequest,
    current_user=Depends(deps.get_current_user),
):
    """
    Recibe la orden del Frontend y se la pasa al Worker.
    """
    usuario_real_id = current_user.id

    print(
        f"🔒 Solicitud autenticada. Usuario: {current_user.email} (ID: {usuario_real_id})"
    )

    task = generar_reporte_pesado_task.delay(
        usuario_real_id, request.reporte_id, request.params, request.formato
    )

    return {
        "mensaje": "La generación del reporte ha comenzado en segundo plano.",
        "task_id": task.id,
        "estado": "Procesando en Celery ⏳",
    }


# --- CONSULTAR ESTADO (Cualquier usuario logueado) ---
@router.get("/task/{task_id}")
def obtener_estado_tarea(task_id: str, current_user=Depends(deps.get_current_user)):
    """
    Consulta el estado de una tarea de Celery usando su ID.
    """
    resultado = celery_app.AsyncResult(task_id)

    if resultado.state == "FAILURE":
        return {"task_id": task_id, "estado": "FAILURE", "error": str(resultado.result)}

    return {
        "task_id": task_id,
        "estado": resultado.status,
        "resultado": resultado.result if resultado.ready() else None,
    }


# --- LISTAR TODOS (Necesario para que el Operador vea el Dropdown) ---
@router.get("/", response_model=List[report_schema.Report])
def read_reports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # Se mantiene acceso general para poder listar en el Generador
    current_user=Depends(deps.get_current_user),
):
    reports = db.query(Report).offset(skip).limit(limit).all() # type: ignore
    return reports


# --- LEER UNO SOLO (Necesario para pintar el formulario dinámico) ---
@router.get("/{report_id}", response_model=report_schema.Report)
def read_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    # Se mantiene acceso general
    current_user=Depends(deps.get_current_user),
):
    # type: ignore - Pylance se confunde con .first()
    report = db.query(Report).filter(Report.id == report_id).first() # type: ignore - Pylance se confunde con .first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report


# =========================================================
# 2. RUTAS ADMINISTRATIVAS (Solo Superuser 🛡️)
# =========================================================


# --- CREAR NUEVO (Solo Admin) ---
@router.post("/", response_model=report_schema.Report)
def create_report(
    *,
    db: Session = Depends(get_db),
    report_in: report_schema.ReportCreate,
    # 🛡️ CAMBIO DE SEGURIDAD: Solo Superuser
    current_user=Depends(deps.get_current_active_superuser),
):
    """
    Crea un nuevo reporte en la base de datos.
    """
    # Convertimos el modelo Pydantic a Diccionario para SQLAlchemy
    report_data = report_in.dict()
    db_report = Report(**report_data)

    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


# --- ACTUALIZAR (Solo Admin) ---
@router.put("/{report_id}", response_model=report_schema.Report)
def update_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    report_in: report_schema.ReportUpdate,
    # 🛡️ CAMBIO DE SEGURIDAD: Solo Superuser
    current_user=Depends(deps.get_current_active_superuser),
):
    """
    Actualiza un reporte existente.
    """
    # type: ignore - Pylance se confunde con .first()
    report = db.query(Report).filter(Report.id == report_id).first() # type: ignore - Pylance se confunde con .first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    update_data = report_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(report, field, value)

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


# --- ELIMINAR (Solo Admin) ---
@router.delete("/{report_id}", response_model=report_schema.Report)
def delete_report(
    *,
    db: Session = Depends(get_db),
    report_id: int,
    # 🛡️ CAMBIO DE SEGURIDAD: Solo Superuser
    current_user=Depends(deps.get_current_active_superuser),
):
    """
    Elimina un reporte de la base de datos.
    """
    # type: ignore - Pylance se confunde con .first()
    report = db.query(Report).filter(Report.id == report_id).first() # type: ignore - Pylance se confunde con .first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    db.delete(report)
    db.commit()
    return report
