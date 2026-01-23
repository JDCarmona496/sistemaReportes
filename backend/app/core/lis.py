import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv  # Necesario para leer el archivo .env
from typing import Any

# Cargar variables del archivo .env
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración Segura (Leyendo desde el .env)
LIS_CONFIG = {
    "host": os.getenv("LIS_HOST", "localhost"),
    "database": os.getenv("LIS_DB", "WINSISLAB"),
    "user": os.getenv("LIS_USER", "postgres"),
    "password": os.getenv("LIS_PASSWORD", ""),
    "port": os.getenv("LIS_PORT", "5432"),
    "connect_timeout": 10,
}

def ejecutar_consulta_lis(sql_query: str, params: Any = None):
    """
    Se conecta al LIS, ejecuta una consulta y devuelve una lista de diccionarios.
    Maneja la apertura y cierre de conexión automáticamente.
    """
    connection = None
    try:
        # 1. Conectar
        connection = psycopg2.connect(**LIS_CONFIG)

        # 2. Cursor que devuelve diccionarios
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # --- PARCHE DE COMPATIBILIDAD (LISTA -> TUPLA) ---
        # Psycopg2 requiere TUPLAS para cláusulas 'IN %(lista)s', 
        # pero JSON/Python suelen enviar LISTAS []. Aquí lo corregimos.
        if params and isinstance(params, dict):
            for k, v in params.items():
                if isinstance(v, list):
                    params[k] = tuple(v)

        # 3. Ejecutar
        if params:
            logger.info(f"🔌 Ejecutando query en LIS con params: {params}")
        else:
            logger.info(f"🔌 Ejecutando query simple en LIS...")

        cursor.execute(sql_query, params)

        # 4. Obtener resultados
        resultados = cursor.fetchall()

        # Convertir a lista normal
        datos_limpios = [dict(row) for row in resultados]

        logger.info(f"✅ Se obtuvieron {len(datos_limpios)} filas del LIS.")
        return datos_limpios

    except Exception as e:
        logger.error(f"❌ Error consultando el LIS: {e}")
        # Es importante relanzar el error para que Celery se entere y marque TASK FAILURE
        raise e

    finally:
        # 5. Siempre cerrar la conexión
        if connection:
            cursor.close()
            connection.close()