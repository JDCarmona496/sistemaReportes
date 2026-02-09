from fastapi import APIRouter

# CORRECCIÓN: Agregamos 'stats' a la lista de imports
from app.api.v1.endpoints import login, users, reports, config, stats, scheduler, system

api_router = APIRouter()

# Rutas de Autenticación (Login)
api_router.include_router(login.router, prefix="/login", tags=["login"])

# Rutas de Usuarios (CRUD)
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Rutas de Reportes (CRUD y Generación)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Rutas de Configuración del Sistema
api_router.include_router(config.router, prefix="/config", tags=["config"])

# Rutas de Estadísticas (Dashboard)
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])

api_router.include_router(system.router, prefix="/system", tags=["system"])
