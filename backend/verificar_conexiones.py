import psycopg2
import os
from dotenv import load_dotenv
import sys

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_db_config(prefix):
    """Construye el diccionario de conexión basado en el prefijo del .env"""
    return {
        "host": os.getenv(f"{prefix}HOST"),
        "database": os.getenv(f"{prefix}DB"),
        "user": os.getenv(f"{prefix}USER"),
        "password": os.getenv(f"{prefix}PASSWORD"),
        "port": os.getenv(f"{prefix}PORT", "5432"),
        "connect_timeout": 3  # Timeout rápido (3s) para diagnóstico ágil
    }

def probar_conexion(sede, prefix):
    print(f"\n📡 PROBANDO CONEXIÓN A: {sede}")
    print("-" * 40)
    
    config = get_db_config(prefix)
    
    # 1. Validación de Configuración
    if not config["host"]:
        print(f"   ⚠️  SKIPPED: No se encontraron credenciales para {prefix}HOST en .env")
        return

    print(f"   🎯 Objetivo: {config['host']}:{config['port']}")
    print(f"   🗄️  Base de Datos: {config['database']}")

    # 2. Intento de Conexión
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Query de prueba ligera
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        conn.close()
        
        # Éxito visual
        print(f"   ✅ ESTADO: CONECTADO")
        print(f"   📝 Motor: {version.split(',')[0]}") # Muestra solo la primera parte de la versión
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ ESTADO: FALLO DE CONEXIÓN")
        print(f"      Error: {str(e).strip()}")
        print("      -> Sugerencia: Verifica que la VPN esté activa y tengas alcance a la IP.")
        
    except Exception as e:
        print(f"   ❌ ERROR CRÍTICO: {e}")

def main():
    print("\n" + "="*60)
    print("      🛠️  DIAGNÓSTICO DE CONECTIVIDAD LIS - BIOLAB SYSTEM")
    print("="*60)

    # Lista de Sedes a probar (Nombre legible, Prefijo en .env)
    sedes = [
        ("SEDE PRINCIPAL (BIOLAB)", "LIS_BIOLAB_"),
        ("SEDE NORTE (BIOSALUD)", "LIS_BIOSALUD_")
    ]

    for nombre, prefijo in sedes:
        probar_conexion(nombre, prefijo)

    print("\n" + "="*60)
    print("Fin del diagnóstico.\n")

if __name__ == "__main__":
    main()