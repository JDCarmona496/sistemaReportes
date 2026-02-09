from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # type: ignore
from app.api import deps
from app.database import get_db
from app.schemas import scheduler as schemas
import json

# Importamos los modelos internos de la librería
from celery_sqlalchemy_scheduler.models import (
    PeriodicTask,
    CrontabSchedule,
    IntervalSchedule,
)

router = APIRouter()


@router.get("/", response_model=List[schemas.PeriodicTask])
def list_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_active_superuser),
):
    """Listar todas las tareas programadas."""
    tasks = db.query(PeriodicTask).all()

    # Mapeo manual rápido para el frontend (aplanamos la estructura)
    resultado = []
    for t in tasks:
        # Usamos # type: ignore para evitar que Pylance confunda
        # las Columnas de SQLAlchemy con los valores reales en tiempo de ejecución.

        # Validación segura de argumentos (JSON Strings -> Listas/Dicts)
        args_data = []
        if t.args:
            try:
                # Forzamos str() para asegurar que json.loads reciba texto
                args_data = json.loads(str(t.args))
            except:
                pass

        kwargs_data = {}
        if t.kwargs:
            try:
                kwargs_data = json.loads(str(t.kwargs))
            except:
                pass

        item = schemas.PeriodicTask(
            id=t.id,  # type: ignore
            name=t.name,  # type: ignore
            task=t.task,  # type: ignore
            args=args_data,
            kwargs=kwargs_data,
            enabled=t.enabled,  # type: ignore
            last_run_at=t.last_run_at,  # type: ignore
            total_run_count=t.total_run_count,  # type: ignore
            # Extraer info del cron (Manejo de nulos con operador ternario)
            crontab_minute=t.crontab.minute if t.crontab else "*",  # type: ignore
            crontab_hour=t.crontab.hour if t.crontab else "*",  # type: ignore
            crontab_day_of_week=t.crontab.day_of_week if t.crontab else "*",  # type: ignore
            crontab_day_of_month=t.crontab.day_of_month if t.crontab else "*",  # type: ignore
            crontab_month_of_year=t.crontab.month_of_year if t.crontab else "*",  # type: ignore
        )
        resultado.append(item)
    return resultado


@router.post("/", response_model=schemas.PeriodicTask)
def create_task(
    task_in: schemas.PeriodicTaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_active_superuser),
):
    """Programar una nueva tarea."""

    # 1. Crear o Buscar el Horario (Crontab)
    schedule = (
        db.query(CrontabSchedule)
        .filter_by(
            minute=task_in.crontab_minute,
            hour=task_in.crontab_hour,
            day_of_week=task_in.crontab_day_of_week,
            day_of_month=task_in.crontab_day_of_month,
            month_of_year=task_in.crontab_month_of_year,
        )
        .first()
    )

    if not schedule:
        schedule = CrontabSchedule(
            minute=task_in.crontab_minute, # type: ignore
            hour=task_in.crontab_hour, # type: ignore
            day_of_week=task_in.crontab_day_of_week, # type: ignore
            day_of_month=task_in.crontab_day_of_month, # type: ignore
            month_of_year=task_in.crontab_month_of_year, # type: ignore
            timezone="America/Bogota", # type: ignore
        )  # type: ignore
        db.add(schedule)
        db.commit()

    # 2. Crear la Tarea
    new_task = PeriodicTask(
        name=task_in.name, # type: ignore
        task=task_in.task, # type: ignore
        crontab=schedule, # type: ignore
        args=json.dumps(task_in.args), # type: ignore
        kwargs=json.dumps(task_in.kwargs), # type: ignore
        enabled=task_in.enabled, # type: ignore
    )  # type: ignore

    db.add(new_task)
    db.commit()

    return list_tasks(db=db, current_user=current_user)[-1]


@router.put("/{task_id}", response_model=schemas.PeriodicTask)
def update_task(
    task_id: int,
    task_in: schemas.PeriodicTaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_active_superuser),
):
    """Actualizar una tarea programada existente."""
    task = db.query(PeriodicTask).filter(PeriodicTask.id == task_id).first()  # type: ignore
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    # 1. Actualizar el horario (Crontab) si cambió
    schedule = (
        db.query(CrontabSchedule)
        .filter_by(
            minute=task_in.crontab_minute,
            hour=task_in.crontab_hour,
            day_of_week=task_in.crontab_day_of_week,
            day_of_month=task_in.crontab_day_of_month,
            month_of_year=task_in.crontab_month_of_year,
        )
        .first()
    )

    if not schedule:
        schedule = CrontabSchedule(
            minute=task_in.crontab_minute, # type: ignore
            hour=task_in.crontab_hour, # type: ignore
            day_of_week=task_in.crontab_day_of_week, # type: ignore
            day_of_month=task_in.crontab_day_of_month, # type: ignore
            month_of_year=task_in.crontab_month_of_year, # type: ignore
            timezone="America/Bogota", # type: ignore
        )  # type: ignore
        db.add(schedule)
        db.commit()

    # 2. Actualizar campos de la tarea
    task.name = task_in.name  # type: ignore
    task.task = task_in.task  # type: ignore
    task.crontab = schedule  # type: ignore
    task.args = json.dumps(task_in.args)  # type: ignore
    task.kwargs = json.dumps(task_in.kwargs)  # type: ignore
    task.enabled = task_in.enabled  # type: ignore

    db.commit()

    # Retornar objeto actualizado con el formato plano
    return schemas.PeriodicTask(
        id=task.id,  # type: ignore
        name=task.name,  # type: ignore
        task=task.task,  # type: ignore
        args=json.loads(str(task.args)) if task.args else [],  # type: ignore
        kwargs=json.loads(str(task.kwargs)) if task.kwargs else {},  # type: ignore
        enabled=task.enabled,  # type: ignore
        last_run_at=task.last_run_at,  # type: ignore
        total_run_count=task.total_run_count,  # type: ignore
        crontab_minute=task.crontab.minute,  # type: ignore
        crontab_hour=task.crontab.hour,  # type: ignore
        crontab_day_of_week=task.crontab.day_of_week,  # type: ignore
        crontab_day_of_month=task.crontab.day_of_month,  # type: ignore
        crontab_month_of_year=task.crontab.month_of_year,  # type: ignore
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_active_superuser),
):
    task = db.query(PeriodicTask).filter(PeriodicTask.id == task_id).first()  # type: ignore
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    db.delete(task)
    db.commit()
    return {"message": "Tarea eliminada"}
