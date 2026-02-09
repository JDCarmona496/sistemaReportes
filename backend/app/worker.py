import time
import logging
import os
import psycopg2
import json  # <--- NUEVO
from datetime import datetime  # <--- NUEVO
import redis  # <--- NUEVO
from celery.exceptions import MaxRetriesExceededError

from app.core.celery_app import celery_app
from app.core.lis import ejecutar_consulta_lis
from app.core.pdf_generator import generar_pdf_universal
from app.core.csv_generator import crear_csv_generico
from app.database import SessionLocal
from app.models.report import Report
from app.models.config import SystemSetting
from app.core.config import settings  # <--- NUEVO
from app.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def obtener_config(db, key, default):
    # type: ignore
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return setting.value if setting else default


# --- FUNCIÓN AUXILIAR: REGISTRAR EN REDIS (HISTORIAL) ---
def registrar_evento_redis(reporte, estado):
    try:
        # Conexión directa a Redis (Síncrona para el worker)
        # Usamos la URL de settings o localhost por defecto
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)

        evento = {
            "reporte": reporte,
            "hora": datetime.now().strftime("%H:%M"),
            "status": estado,
        }

        # Guardar en la lista 'global_history' (La misma que lee el Dashboard)
        r.lpush("global_history", json.dumps(evento))
        r.ltrim("global_history", 0, 19)  # Mantener solo los últimos 20

        # Incrementar contador para gráfica (Opcional, si usas otra key)
        # r.incr("stats:total_reports")

    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar historial en Redis: {e}")


# --- TAREA 1: GENERACIÓN DE REPORTES ---
@celery_app.task(bind=True, acks_late=True, max_retries=2)
def generar_reporte_pesado_task(
    self,
    usuario_id: int,
    reporte_id: int,
    params: dict,
    formato: str = "PDF",
    sede: str = "BIOLAB",
):
    logger.info(f"📄 [WORKER] Iniciando tarea ID {reporte_id}. Sede: {sede}.")

    db = SessionLocal()
    try:
        reporte_db = db.query(Report).filter(Report.id == reporte_id).first()  # type: ignore
        if not reporte_db:
            registrar_evento_redis(f"Reporte #{reporte_id}", "ERROR")  # Log Fallo
            return {"status": "error", "error": "Reporte no encontrado"}

        sql_query = str(reporte_db.sql_query)
        titulo_base = str(reporte_db.title)
        tipo_layout = getattr(reporte_db, "layout", "tabla") or "tabla"

        # --- CONSULTA LIS ---
        datos = ejecutar_consulta_lis(sql_query, params, sede=sede)

        if not datos:
            # Registrar Intento Fallido (Sin datos)
            registrar_evento_redis(f"{titulo_base} ({sede})", "VACÍO")
            return {
                "status": "skipped",
                "mensaje": f"Sin datos para los filtros en {sede}",
                "url_descarga": None,
            }

        logger.info(f"📊 Datos: {len(datos)} registros")

        # --- GENERACIÓN ---
        titulo_completo = f"[{sede}] {titulo_base}"
        url_archivo = None

        if formato.upper() == "CSV":
            url_archivo = crear_csv_generico(datos, titulo_completo, usuario_id)
        else:
            url_archivo = generar_pdf_universal(
                datos, titulo_completo, usuario_id, layout_type=tipo_layout
            )

        if not url_archivo:
            registrar_evento_redis(f"{titulo_base} ({sede})", "ERROR")
            return {"status": "error", "error": "Fallo al escribir archivo."}

        logger.info(f"✅ Archivo generado: {url_archivo}")

        # --- REGISTRO EXITOSO EN REDIS ---
        registrar_evento_redis(f"{titulo_base} ({sede})", "OK")

        return {
            "status": "success",
            "archivo": url_archivo.split("/")[-1],
            "url_descarga": url_archivo,
            "total_registros": len(datos),
            "formato": formato,
            "sede": sede,
            "datos_preview": datos[:5],
        }

    except (psycopg2.OperationalError, ValueError) as e:
        try:
            wait_time = 2**self.request.retries
            logger.warning(f"⚠️ {sede} no responde. Reintentando...")
            raise self.retry(exc=e, countdown=wait_time)
        except MaxRetriesExceededError:
            # Registrar Offline
            registrar_evento_redis(f"Reporte #{reporte_id} ({sede})", "OFFLINE")
            return {
                "status": "skipped",
                "mensaje": f"Sin conexión {sede}",
                "url_descarga": None,
            }

    except Exception as e:
        logger.exception(f"❌ Error crítico: {e}")
        registrar_evento_redis(f"Reporte #{reporte_id}", "CRASH")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


# --- TAREA 2: LIMPIEZA (Igual que antes) ---
@celery_app.task
def limpiar_reportes_antiguos_task():
    # ... (El código de limpieza se mantiene igual) ...
    # Solo copiamos la parte inicial para brevedad, mantén tu lógica de borrado aquí
    directorio = "static/reports"
    ahora = time.time()
    db = SessionLocal()
    horas = 24
    try:
        horas_str = obtener_config(db, "worker_retention_hours", "24")
        horas = int(str(horas_str)) if str(horas_str).isdigit() else 24
    except:
        pass
    finally:
        db.close()

    if not os.path.exists(directorio):
        return "No dir"

    c = 0
    for f in os.listdir(directorio):
        p = os.path.join(directorio, f)
        if os.path.isfile(p) and (ahora - os.path.getmtime(p)) > horas * 3600:
            try:
                os.remove(p)
                c += 1
            except:
                pass

    return f"Limpieza OK: {c}"

