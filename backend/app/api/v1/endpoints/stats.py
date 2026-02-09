from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session # type: ignore
import json
from collections import Counter
import redis.asyncio as redis

from app.api import deps

# CORRECCIÓN 1: Importamos get_redis_client desde core, que es su casa real
from app.core.deps import get_redis_client
from app.database import get_db
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/")
async def get_stats(
    db: Session = Depends(get_db),
    current_user=Depends(deps.get_current_user),
    # CORRECCIÓN 1: Usamos la función importada directamente
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """
    Retorna estadísticas en tiempo real para el Dashboard.
    1. Conteo de usuarios (SQL)
    2. Actividad reciente de reportes (Redis)
    """

    # 1. Estadísticas de Usuarios (SQL)
    total_users = db.query(UserModel).count()
    admins = db.query(UserModel).filter(UserModel.is_superuser == True).count() # type: ignore
    operators = total_users - admins

    # 2. Estadísticas de Uso (Redis)
    # Traemos los últimos 100 eventos del historial global
    # CORRECCIÓN 2: Agregamos # type: ignore para que Pylance sepa que esto es awaitable
    historial_raw = await redis_client.lrange("global_history", 0, 99)  # type: ignore

    # Procesamos: Contar cuántas veces se genera cada reporte
    nombres_reportes = []
    for item in historial_raw:
        try:
            data = json.loads(item)
            # Extraemos el nombre del reporte.
            if "reporte" in data:
                nombres_reportes.append(data["reporte"])
        except:
            continue

    # Usamos Counter para contar repeticiones
    conteo = Counter(nombres_reportes)

    # Preparamos datos para Chart.js
    if not conteo:
        top_labels = []
        top_values = []
    else:
        # Tomamos los 5 más frecuentes para no saturar la gráfica
        comunes = conteo.most_common(5)
        top_labels = [item[0] for item in comunes]
        top_values = [item[1] for item in comunes]

    return {
        "users": {"admins": admins, "operators": operators},
        "activity": {"labels": top_labels, "data": top_values},
    }
