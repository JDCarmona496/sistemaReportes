import os
import sys
from celery import Celery
from celery.signals import (
    setup_logging,
    beat_init,
)  # <--- IMPORTANTE: Importar beat_init
from app.core.config import settings
from app.core.logging_config import configure_logging

# Creación de la instancia Celery
celery_app = Celery(
    "worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

# Configuración Maestra
celery_app.conf.update(
    # Serialización segura (JSON)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Zona Horaria
    timezone="America/Bogota",
    enable_utc=True,
    # --- SCHEDULER DINÁMICO (BASE DE DATOS) ---
    beat_scheduler="celery_sqlalchemy_scheduler.schedulers:DatabaseScheduler",
    # Conexión específica para el Scheduler
    beat_dburi=settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
)


# ==============================================================================
# CONFIGURACIÓN DE LOGS (WINDOWS SAFE)
# ==============================================================================
@setup_logging.connect
def config_loggers(*args, **kwargs):
    configure_logging()


# ==============================================================================
# PARCHE DE COMPATIBILIDAD (ELIMINAR TAREA CONFLICTIVA)
# ==============================================================================
# La tarea 'celery.backend_cleanup' intenta escribirse en la BD usando un objeto
# de zona horaria incompatible con la librería del scheduler.
# Como Redis gestiona la expiración nativamente, eliminamos esta tarea al iniciar.
@beat_init.connect
def on_beat_init(sender, **kwargs):
    try:
        scheduler = sender.scheduler
        # Accedemos al horario interno y borramos la tarea si existe
        if "celery.backend_cleanup" in scheduler.schedule:
            del scheduler.schedule["celery.backend_cleanup"]
            print(
                "🔧 [FIX] Tarea 'celery.backend_cleanup' eliminada para evitar error de ZoneInfo."
            )
    except Exception as e:
        print(f"⚠️ No se pudo aplicar el parche de limpieza: {e}")
