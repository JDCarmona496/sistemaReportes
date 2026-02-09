from fastapi import APIRouter

# Importamos todos los endpoints de la aplicación
from app.api.v1.endpoints import (
    login,
    users,
    reports,
    config,
    stats,
    scheduler,
    system,
)

api_router = APIRouter()

# 1. Autenticación (Login)
api_router.include_router(login.router, prefix="/login", tags=["login"])

# 2. Gestión de Usuarios (CRUD)
api_router.include_router(users.router, prefix="/users", tags=["users"])

# 3. Reportes (Generación y Configuración)
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# 4. Configuración Global del Sistema
api_router.include_router(config.router, prefix="/config", tags=["config"])

# 5. Estadísticas para el Dashboard
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

# 6. Programador de Tareas (Celery Beat)
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])

# 7. Diagnóstico y Salud del Sistema (Ping LIS)
api_router.include_router(system.router, prefix="/system", tags=["system"])
