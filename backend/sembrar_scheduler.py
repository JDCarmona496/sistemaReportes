from app.database import SessionLocal

# Importamos los modelos de la librería externa
from celery_sqlalchemy_scheduler.models import PeriodicTask, CrontabSchedule
import json


def sembrar_tareas():
    db = SessionLocal()
    print("🌱 Sembrando tareas programadas...")

    # ------------------------------------------------------------------
    # 1. CREAR HORARIOS (CRON)
    # CORRECCIÓN: Usar STRINGS para hora/minuto, no enteros.
    # ------------------------------------------------------------------

    # Horario: Todos los días a las 3:00 AM
    # Nota el uso de comillas: hour="3", minute="0"
    schedule_madrugada = (
        db.query(CrontabSchedule).filter_by(hour="3", minute="0").first()
    )
    if not schedule_madrugada:
        # type: ignore -> Silencia "Ningún parámetro llamado hour/minute..."
        schedule_madrugada = CrontabSchedule(
            hour="3", # type: ignore
            minute="0", # type: ignore
            day_of_week="*", # type: ignore
            day_of_month="*", # type: ignore
            month_of_year="*",# type: ignore
            timezone="America/Bogota", # type: ignore
        )
        db.add(schedule_madrugada)
        db.commit()

    # Horario: Todos los Lunes a las 8:00 AM
    schedule_lunes = (
        db.query(CrontabSchedule)
        .filter_by(hour="8", minute="0", day_of_week="1")
        .first()
    )
    if not schedule_lunes:
        # type: ignore -> Silencia errores de Pylance
        schedule_lunes = CrontabSchedule(
            hour="8", # type: ignore
            minute="0", # type: ignore
            day_of_week="1",  # type: ignore
            timezone="America/Bogota", # type: ignore
        )
        db.add(schedule_lunes)
        db.commit()

    # ------------------------------------------------------------------
    # 2. CREAR TAREAS (PeriodicTask)
    # ------------------------------------------------------------------

    # TAREA A: Limpieza Automática
    tarea_limpieza = (
        db.query(PeriodicTask)
        .filter_by(name="Mantenimiento: Limpieza Archivos")
        .first()
    )
    if not tarea_limpieza:
        # type: ignore -> Silencia errores de Pylance sobre 'name', 'task', etc.
        tarea_limpieza = PeriodicTask(
            name="Mantenimiento: Limpieza Archivos", # type: ignore
            task="app.worker.limpiar_reportes_antiguos_task", # type: ignore
            crontab=schedule_madrugada, # type: ignore
            enabled=True, # type: ignore
            description="Borra reportes generados hace más de 24h.", # type: ignore
        )
        db.add(tarea_limpieza)
        print("✅ Tarea 'Limpieza' creada.")
    else:
        print("ℹ️ Tarea 'Limpieza' ya existía.")

    # TAREA B: Ejemplo de Reporte Automático
    tarea_reporte = (
        db.query(PeriodicTask).filter_by(name="Reporte Semanal Automático").first()
    )
    if not tarea_reporte:
        args_json = json.dumps([1, 1, {"lista_pacientes": ["80007070"]}, "PDF"])

        # type: ignore -> Silencia errores de Pylance
        tarea_reporte = PeriodicTask(
            name="Reporte Semanal Automático", # type: ignore
            task="app.worker.generar_reporte_pesado_task", # type: ignore
            crontab=schedule_lunes, # type: ignore
            args=args_json, # type: ignore
            enabled=False, # type: ignore
            description="Ejemplo semanal.", # type: ignore
        )
        db.add(tarea_reporte)
        print("✅ Tarea 'Reporte Semanal' creada.")

    db.commit()
    db.close()
    print("✨ Proceso de siembra finalizado sin errores de tipo.")


if __name__ == "__main__":
    sembrar_tareas()
