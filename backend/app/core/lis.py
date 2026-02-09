import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from dotenv import load_dotenv
from typing import Any
import re

load_dotenv()

logger = logging.getLogger(__name__)


def get_lis_config(sede: str):
    """
    Construye la configuración de conexión dinámicamente según la sede.
    """
    prefix = f"LIS_{sede.upper()}_"

    return {
        "host": os.getenv(f"{prefix}HOST"),
        "database": os.getenv(f"{prefix}DB"),
        "user": os.getenv(f"{prefix}USER"),
        "password": os.getenv(f"{prefix}PASSWORD"),
        "port": os.getenv(f"{prefix}PORT", "5432"),
        "connect_timeout": 10,
    }


# --- FUNCIÓN DE SALUD (PING) ---
def verificar_conexion_lis(sede: str = "BIOLAB"):
    """
    Intenta hacer un 'Ping' rápido a la base de datos.
    Retorna: (bool, str) -> (Online?, Mensaje)
    """
    conn = None
    try:
        config = get_lis_config(sede)

        # Si no hay configuración IP, fallamos rápido
        if not config["host"]:
            return False, f"Sin config para {sede}"

        # Timeout agresivo (2s) para no bloquear el dashboard
        ping_config = config.copy()
        ping_config["connect_timeout"] = 2

        conn = psycopg2.connect(**ping_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # La consulta más liviana posible
        conn.close()

        return True, "Online"
    except Exception as e:
        return False, str(e)
    finally:
        if conn and not conn.closed:
            conn.close()


def ejecutar_consulta_lis(sql_query: str, params: Any = None, sede: str = "BIOLAB"):
    """
    Ejecuta consulta en la sede especificada.
    """
    connection = None
    cursor = None
    db_config = get_lis_config(sede)

    try:
        if not db_config["host"]:
            raise ValueError(f"Configuración no encontrada para {sede}")

        logger.info(f"🔌 Conectando a sede: {sede} ({db_config['host']})")
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        if params and isinstance(params, dict):
            sql_query = re.sub(r":([a-zA-Z0-9_]+)", r"%(\1)s", sql_query)
            for k, v in params.items():
                if isinstance(v, list):
                    params[k] = tuple(v)

        cursor.execute(sql_query, params)
        resultados = cursor.fetchall()
        datos_limpios = [dict(row) for row in resultados]

        logger.info(f"✅ [{sede}] Se obtuvieron {len(datos_limpios)} filas.")
        return datos_limpios

    except Exception as e:
        logger.error(f"❌ Error consultando LIS ({sede}): {e}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
