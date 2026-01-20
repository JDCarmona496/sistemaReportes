from fastapi import APIRouter
from app.api.v1.endpoints import login, users, reports # <--- Importar reports

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"]) # <--- Conectar