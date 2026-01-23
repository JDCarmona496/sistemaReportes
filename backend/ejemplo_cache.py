import redis
import time
import json

# 1. Conexión a Redis (Igual que en tu test)
cache = redis.Redis(host="localhost", port=6379, decode_responses=True)


def obtener_reporte_pesado(fecha):
    clave_cache = f"reporte:{fecha}"

    print(f"--> Buscando reporte del {fecha}...")

    # 1. Obtenemos el dato (Pylance aquí tiene dudas del tipo)
    datos_guardados = cache.get(clave_cache)

    # 2. Hacemos el "Type Guard" (Validación de tipo)
    # Esto le confirma a Pylance que 'datos_guardados' es seguro de usar
    if datos_guardados is not None and isinstance(datos_guardados, str):
        print("⚡ ¡RÁPIDO! Datos encontrados en Redis (Caché).")
        return json.loads(datos_guardados)

    # PASO B: Si no existe, lo calculamos (Simulación de trabajo pesado)
    print("🐢 LENTO... Calculando reporte desde cero (Consulta BD)...")
    time.sleep(3)  # Simulamos demora de 3 segundos

    resultado = {
        "fecha": fecha,
        "ventas": 5000,
        "estado": "completado",
        "generado_por": "sistema_backend",
    }

    # PASO C: Guardamos el resultado en Redis por 60 segundos (TTL)
    # 'ex=60' significa que en 1 minuto se borra solo para mantener datos frescos.
    cache.set(clave_cache, json.dumps(resultado), ex=60)

    return resultado


# --- ZONA DE PRUEBAS ---

# Primera vez: Debería tardar 3 segundos
inicio = time.time()
print(obtener_reporte_pesado("2023-10-27"))
print(f"Tiempo total 1ra vez: {time.time() - inicio:.2f} segundos\n")

# Segunda vez: Debería ser instantáneo (0.0 segundos)
inicio = time.time()
print(obtener_reporte_pesado("2023-10-27"))
print(f"Tiempo total 2da vez: {time.time() - inicio:.2f} segundos")
