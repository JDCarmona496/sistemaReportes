import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv
from typing import Any
import re

load_dotenv()

logger = logging.getLogger(__name__)

LIS_CONFIG = {
    "host": os.getenv("LIS_HOST", "localhost"),
    "database": os.getenv("LIS_DB", "WINSISLAB"),
    "user": os.getenv("LIS_USER", "postgres"),
    "password": os.getenv("LIS_PASSWORD", ""),
    "port": os.getenv("LIS_PORT", "5432"),
    "connect_timeout": 10,
}


# --- NUEVA FUNCIÓN: Verificar Estado ---
def verificar_conexion_lis():
    """
    Intenta hacer un 'Ping' a la base de datos externa.
    Retorna: (bool, str) -> (Exito, Mensaje/Latencia)
    """
    conn = None
    try:
        # Hacemos una copia de la config para bajar el timeout solo para esta prueba
        # Si la VPN está caída, no queremos esperar 10s, queremos saberlo YA (2s).
        ping_config = LIS_CONFIG.copy()
        ping_config["connect_timeout"] = 2

        conn = psycopg2.connect(**ping_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Consulta más ligera posible
        conn.close()

        return True, "En Línea"
    except psycopg2.OperationalError as e:
        return False, "Sin Conexión (VPN/Red)"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conn and not conn.closed:
            conn.close()


# ... (Tu función ejecutar_consulta_lis sigue igual abajo) ...
def ejecutar_consulta_lis(sql_query: str, params: Any = None):
    """
    Se conecta al LIS, ejecuta una consulta y devuelve una lista de diccionarios.
    Maneja la apertura y cierre de conexión automáticamente.
    Traduce sintaxis :param a %(param)s para compatibilidad con Psycopg2.
    """
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(**LIS_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        if params and isinstance(params, dict):
            sql_query = re.sub(r":([a-zA-Z0-9_]+)", r"%(\1)s", sql_query)

        if params and isinstance(params, dict):
            for k, v in params.items():
                if isinstance(v, list):
                    params[k] = tuple(v)

        if params:
            logger.info(f"🔌 Ejecutando query en LIS: {sql_query}")
            logger.info(f"🔌 Params: {params}")
        else:
            logger.info(f"🔌 Ejecutando query simple en LIS...")

        cursor.execute(sql_query, params)
        resultados = cursor.fetchall()
        datos_limpios = [dict(row) for row in resultados]

        logger.info(f"✅ Se obtuvieron {len(datos_limpios)} filas del LIS.")
        return datos_limpios

    except Exception as e:
        logger.error(f"❌ Error consultando el LIS: {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
