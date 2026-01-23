import redis

# Nota que usamos 'localhost' y el puerto por defecto 6379
# Aunque Redis vive en Linux, Windows lo ve localmente.
try:
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Guardamos un dato
    client.set('prueba_sistema', '¡Funcionando desde Windows!')

    # Recuperamos el dato
    valor = client.get('prueba_sistema')

    print(f"Éxito: Redis respondió -> {valor}")

except Exception as e:
    print(f"Error de conexión: {e}")