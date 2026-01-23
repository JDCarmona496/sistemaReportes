import psycopg2
from psycopg2 import OperationalError
import sys

# --- TUS CREDENCIALES DE PRUEBA ---
# Nota: En producción, esto irá en un archivo .env, no en el código.
LIS_CONFIG = {
    "host": "192.168.61.27",
    "database": "WINSISLAB",
    "user": "postgres",
    "password": "u2Bi55+Win",
    "port": "5432",
    "connect_timeout": 5  # Si en 5s no responde, cancelamos.
}

def probar_conexion():
    print(f"📡 Intentando conectar a {LIS_CONFIG['host']}::{LIS_CONFIG['database']}...")
    print("   (Asegúrate de que tu VPN esté ENCENDIDA)")

    try:
        # 1. Intentamos abrir la conexión
        connection = psycopg2.connect(**LIS_CONFIG)
        
        # 2. Creamos un cursor para hablar con la BD
        cursor = connection.cursor()
        
        # 3. Ejecutamos una consulta muy simple (ping)
        print("✅ Conexión TCP establecida. Verificando versión de BD...")
        cursor.execute("SELECT version();")
        
        # 4. Obtenemos el resultado
        db_version = cursor.fetchone()
        
        print(f"\n🎉 ¡ÉXITO ROTUNDO! Estás conectado al LIS.")
        print(f"📌 Versión del Motor: {db_version[0]}")
        
        # Limpieza
        cursor.close()
        connection.close()
        return True

    except OperationalError as e:
        print("\n❌ FALLÓ LA CONEXIÓN (Error Operacional)")
        print(f"Detalle: {e}")
        print("\n--- POSIBLES CAUSAS EN WSL ---")
        print("1. La VPN está apagada.")
        print("2. WSL2 no está viendo la VPN de Windows (Problema común de redes).")
        print("3. La IP o el puerto son incorrectos.")
        return False

    except Exception as e:
        print(f"\n❌ ERROR DESCONOCIDO: {e}")
        return False

if __name__ == "__main__":
    exito = probar_conexion()
    if not exito:
        sys.exit(1)