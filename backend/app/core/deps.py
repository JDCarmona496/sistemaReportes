# app/dependencies.py
import redis.asyncio as redis

# Configuración del Pool (El "tanque" de conexiones)
redis_pool = redis.ConnectionPool.from_url(
    "redis://localhost", 
    decode_responses=True, 
    encoding="utf-8"
)

async def get_redis_client():
    """
    Generador que entrega una conexión y asegura que se cierre al terminar.
    """
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        # Esto se ejecuta SIEMPRE al terminar la petición, haya error o no.
        await client.close()