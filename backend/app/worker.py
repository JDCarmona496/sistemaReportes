import time
import logging
import os
from app.core.celery_app import celery_app
from app.core.lis import ejecutar_consulta_lis

# Importamos la función MAESTRA que decide el diseño
from app.core.pdf_generator import generar_pdf_universal
from app.core.csv_generator import crear_csv_generico
from app.database import SessionLocal
from app.models.report import Report

# Inicializamos el logger
logger = logging.getLogger(__name__)


# --- TAREA 1: GENERACIÓN DE REPORTES ---
@celery_app.task(acks_late=True)
def generar_reporte_pesado_task(
    usuario_id: int, reporte_id: int, params: dict, formato: str = "PDF"
):

    logger.info(
        f"📄 [WORKER] Iniciando tarea reporte ID {reporte_id}. Formato: {formato}"
    )

    db = SessionLocal()
    try:
        reporte_db = db.query(Report).filter(Report.id == reporte_id).first()
        if not reporte_db:
            logger.error(f"❌ Reporte {reporte_id} no encontrado en base de datos.")
            return {"error": "Reporte no encontrado"}

        sql_query = str(reporte_db.sql_query)
        titulo = str(reporte_db.title)

        # OBTENEMOS EL LAYOUT DE LA BD (Si es nulo, usamos 'tabla' por defecto)
        # Esto permite que unos reportes salgan como Ficha y otros como Tabla
        tipo_layout = getattr(reporte_db, "layout", "tabla") or "tabla"

        # Consultar LIS
        datos = ejecutar_consulta_lis(sql_query, params)
        logger.info(f"📊 Datos obtenidos del LIS: {len(datos)} registros")

        if not datos:
            return {"archivo": "Vacio.txt", "mensaje": "Sin datos"}

        # DECISIÓN: ¿PDF o CSV?
        url_archivo = None

        if formato.upper() == "CSV":
            url_archivo = crear_csv_generico(datos, titulo, usuario_id)
        else:
            # --- CAMBIO CLAVE AQUÍ ---
            # Usamos la función universal y le pasamos el layout de la BD
            logger.info(f"🎨 Generando PDF con diseño: {tipo_layout}")
            url_archivo = generar_pdf_universal(
                datos, titulo, usuario_id, layout_type=tipo_layout
            )

        if not url_archivo:
            logger.error("❌ La función generadora devolvió None.")
            return {"error": "Error generando el archivo."}

        logger.info(f"✅ Archivo generado: {url_archivo}")

        return {
            "archivo": url_archivo.split("/")[-1],
            "url_descarga": url_archivo,
            "total_registros": len(datos),
            "formato": formato,
            "datos_preview": datos[:5],
        }

    except Exception as e:
        logger.exception(f"❌ Excepción crítica en worker: {e}")
        return {"error": str(e)}
    finally:
        db.close()


# --- TAREA 2: MANTENIMIENTO (LIMPIEZA) ---
@celery_app.task
def limpiar_reportes_antiguos_task():
    """
    Elimina archivos de la carpeta static/reports que sean más viejos de 24 horas.
    """
    directorio = "static/reports"
    ahora = time.time()
    limite_tiempo = 24 * 3600  # 24 Horas

    contador = 0
    errores = 0

    if not os.path.exists(directorio):
        logger.warning("⚠️ Directorio static/reports no existe, saltando limpieza.")
        return "Directorio no encontrado"

    logger.info("🧹 [MANTENIMIENTO] Iniciando limpieza de archivos antiguos...")

    for archivo in os.listdir(directorio):
        ruta_completa = os.path.join(directorio, archivo)

        if os.path.isfile(ruta_completa):
            try:
                tiempo_archivo = os.path.getmtime(ruta_completa)

                # Si es viejo, borrar
                if (ahora - tiempo_archivo) > limite_tiempo:
                    os.remove(ruta_completa)
                    contador += 1
                    logger.info(f"🗑️ Eliminado por antigüedad: {archivo}")
            except Exception as e:
                logger.error(f"❌ Error eliminando {archivo}: {e}")
                errores += 1

    resultado = f"✅ Limpieza terminada. Eliminados: {contador}. Errores: {errores}."
    logger.info(resultado)
    return resultado
