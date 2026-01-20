from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router  # <--- Importamos el router
from app.database import engine, Base
from app.models import user 

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Incluimos todas las rutas de la V1 (como el login)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def leer_raiz():
    return {"mensaje": "Sistema de Reportes Activo"}