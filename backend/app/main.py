from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import os

# Importaciones Propias
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.core.deps import get_redis_client

# Librerías estándar
import json
import asyncio
import redis.asyncio as redis
from datetime import datetime

# ------------------------------------------------------
# 1. CONFIGURACIÓN DE LOGS (Antes de crear la app)
# ------------------------------------------------------
configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# ------------------------------------------------------
# 2. CONFIGURACIÓN CORS (Seguridad)
# ------------------------------------------------------
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ------------------------------------------------------
# 3. ARCHIVOS ESTÁTICOS Y FAVICON
# ------------------------------------------------------
# Montar carpeta static para CSS/JS/Imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")


# Evitar error 404 del navegador buscando el icono
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Si tienes un archivo favicon.ico en static, úsalo. Si no, retorna vacío o uno genérico.
    file_path = "static/favicon.ico"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("static/css/styles.css")  # Dummy response si no existe imagen


# ------------------------------------------------------
# 4. RUTAS DE LA API (Backend)
# ------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)

# ------------------------------------------------------
# 5. RUTAS DEL FRONTEND (Vistas HTML)
# ------------------------------------------------------


@app.get("/")
async def view_login():
    """Ruta raíz: Muestra el Login"""
    return FileResponse("static/login.html")


@app.get("/dashboard")
async def view_dashboard():
    """Ruta Dashboard: La app principal"""
    return FileResponse("static/dashboard.html")


# ------------------------------------------------------
# 6. ENDPOINTS EXTRA (Historial y Pruebas Redis)
# ------------------------------------------------------
MAX_HISTORIAL = 20


@app.get("/historial")
async def ver_historial_dashboard(
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """
    Recupera los últimos eventos (reportes generados) desde Redis.
    """
    # type: ignore - Pylance no detecta bien los métodos async de redis
    lista_raw = await redis_client.lrange("global_history", 0, -1) # type: ignore

    historial_limpio = []
    for item in lista_raw:
        try:
            historial_limpio.append(json.loads(item))
        except:
            continue

    return {"cantidad": len(historial_limpio), "ultimos_eventos": historial_limpio}


# (Opcional) Endpoint de prueba para simular actividad manual sin Worker
@app.get("/reporte-pro/{fecha}")
async def obtener_reporte_pro(
    fecha: str, redis_client: redis.Redis = Depends(get_redis_client)
):
    clave = f"reporte:{fecha}"

    # 1. Caché
    datos = await redis_client.get(clave)
    if datos:
        return {"fuente": "⚡ CACHÉ (Redis)", "data": json.loads(datos)}

    # 2. Simulación
    await asyncio.sleep(2)
    payload = {"fecha": fecha, "ts": datetime.now().timestamp()}

    # 3. Guardar
    await redis_client.set(clave, json.dumps(payload), ex=60)

    # Historial
    item = {
        "reporte": f"Reporte {fecha}",
        "hora": datetime.now().strftime("%H:%M:%S"),
        "status": "OK",
    }
    await redis_client.lpush("global_history", json.dumps(item))  # type: ignore
    await redis_client.ltrim("global_history", 0, MAX_HISTORIAL)  # type: ignore

    return {"fuente": "🐢 DB", "data": payload}


# ------------------------------------------------------
# 7. EVENTOS DE INICIO
# ------------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("\n📍 RUTAS ACTIVAS:")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"   ➡️  {route.path}")  # type: ignore
    print("\n")
