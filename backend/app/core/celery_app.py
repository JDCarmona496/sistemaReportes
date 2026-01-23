from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging  # <--- 1. Importar Señal
from app.core.config import settings
from app.core.logging_config import configure_logging  # <--- 2. Importar tu config

# Creamos la instancia de Celery
celery_app = Celery(
    "worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

# Configuración General
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
)


# --- 3. EL TRUCO MAESTRO ---
# Esta función se ejecuta JUSTO cuando Celery intenta configurar sus logs.
# Al conectarnos a esta señal, evitamos que Celery imponga su configuración por defecto
# y en su lugar usamos la nuestra (que guarda en archivo).
@setup_logging.connect
def config_loggers(*args, **kwargs):
    configure_logging()


# Configuración del Cronograma (Beat)
celery_app.conf.beat_schedule = {
    "limpiar-reportes-diario": {
        "task": "app.worker.limpiar_reportes_antiguos_task",
        "schedule": crontab(minute=0, hour=3),
    },
}
