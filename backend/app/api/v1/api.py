from fastapi import APIRouter
from app.api.v1.endpoints import login, users, reports

api_router = APIRouter()
# Aquí añadimos /login
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])